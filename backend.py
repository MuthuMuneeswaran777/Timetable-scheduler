"""
Smart Class Scheduler Backend
FastAPI application for generating optimized timetables for higher education institutions.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, time
from jose import JWTError, jwt
from passlib.context import CryptContext
import mysql.connector
from mysql.connector import Error
import random
import json
from enum import Enum
import os
from dotenv import load_dotenv
from functools import lru_cache
import asyncio

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'smart_class_scheduler')
}

# JWT Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI app
app = FastAPI(
    title="Smart Class Scheduler API",
    description="API for generating optimized timetables",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str

class UserCreate(UserBase):
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: int
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class ClassroomBase(BaseModel):
    name: str
    capacity: int
    building: Optional[str] = None
    floor: Optional[int] = None
    has_projector: bool = False
    has_computer: bool = False

class Classroom(ClassroomBase):
    id: int
    created_at: datetime

class FacultyBase(BaseModel):
    name: str
    email: EmailStr
    department: str
    phone: Optional[str] = None
    max_hours_per_day: int = 8
    max_hours_per_week: int = 40

class Faculty(FacultyBase):
    id: int
    created_at: datetime

class SubjectBase(BaseModel):
    code: str
    name: str
    department: str
    credit_hours: int
    semester: int
    year: int
    is_lab: bool = False
    requires_special_equipment: bool = False

class Subject(SubjectBase):
    id: int
    created_at: datetime

class TimetableBase(BaseModel):
    name: str
    academic_year: str
    semester: str

class Timetable(TimetableBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    approved_at: Optional[datetime] = None
    locked_at: Optional[datetime] = None

class ScheduleEntryBase(BaseModel):
    subject_id: int
    faculty_id: int
    classroom_id: int
    day_of_week: str
    start_time: str
    end_time: str

class ScheduleEntry(ScheduleEntryBase):
    id: int
    timetable_id: int
    created_at: datetime

class ScheduleRequest(BaseModel):
    academic_year: str
    semester: str
    subjects: List[int]  # List of subject IDs to schedule
    constraints: Optional[Dict[str, Any]] = {}

class TimetableOption(BaseModel):
    id: int
    name: str
    schedule: List[ScheduleEntry]
    score: float
    conflicts: List[str]

# Database connection with connection pooling
import mysql.connector.pooling

# Create connection pool for better efficiency
try:
    # Test connection first
    test_conn = mysql.connector.connect(**DB_CONFIG)
    test_conn.close()
    
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="smart_scheduler_pool",
        pool_size=5,
        pool_reset_session=True,
        **DB_CONFIG
    )
    DATABASE_AVAILABLE = True
    print("✅ Database connection pool created successfully")
except mysql.connector.Error as err:
    print(f"❌ Database connection pool error: {err}")
    print("🔄 Running in DEMO MODE with mock data")
    print("💡 To fix: Install MySQL or check DATABASE_SETUP_GUIDE.txt")
    connection_pool = None
    DATABASE_AVAILABLE = False
except Exception as e:
    print(f"❌ Unexpected database error: {e}")
    print("🔄 Running in DEMO MODE with mock data")
    connection_pool = None
    DATABASE_AVAILABLE = False

def get_db():
    # Try direct connection first, then pool
    try:
        # Direct connection approach
        db = mysql.connector.connect(**DB_CONFIG)
        yield db
    except mysql.connector.Error as err:
        print(f"Direct connection failed: {err}")
        # Try connection pool as fallback
        if DATABASE_AVAILABLE and connection_pool:
            db = None
            try:
                db = connection_pool.get_connection()
                yield db
            except mysql.connector.Error as err:
                print(f"Pool connection error: {err}")
                yield None
            except Exception as e:
                print(f"Unexpected database error: {e}")
                yield None
            finally:
                if db is not None and db.is_connected():
                    db.close()
        else:
            yield None
    except Exception as e:
        print(f"Connection error: {e}")
        yield None
    finally:
        if 'db' in locals() and db is not None and db.is_connected():
            db.close()

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Get user from database
    try:
        db = next(get_db())
        user = get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        print(f"Error getting current user: {e}")
        raise credentials_exception

def get_user_by_username(db, username: str):
    if db is None:
        # Mock user for demo when database is not available
        # Use a pre-computed hash for 'password123' to avoid generating new hash each time
        password_hash = '$2b$12$ycokfWERAVNYLSCmWgzcBuCL3'
        
        if username == "admin1":
            return {
                'id': 1,
                'username': 'admin1',
                'email': 'admin@university.edu',
                'password_hash': password_hash,
                'role': 'admin',
                'full_name': 'S.M.Poobalan',
                'created_at': datetime.now()
            }
        elif username == "faculty1":
            return {
                'id': 2,
                'username': 'faculty1',
                'email': 'prof.smith@university.edu',
                'password_hash': password_hash,
                'role': 'faculty',
                'full_name': 'Prof. John Smith',
                'created_at': datetime.now()
            }
        elif username == "student1":
            return {
                'id': 3,
                'username': 'student1',
                'email': 'student1@university.edu',
                'password_hash': password_hash,
                'role': 'student',
                'full_name': 'John Doe',
                'created_at': datetime.now()
            }
        return None
    
    try:
        print(f"🔍 Querying database for user: {username}")
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        result = cursor.fetchone()
        print(f"📊 Query result: {'Found' if result else 'Not found'}")
        return result
    except Exception as e:
        print(f"❌ Database query error: {e}")
        return None

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        print(f"🔐 Login attempt for user: {form_data.username}")
        db = next(get_db())
        print(f"📊 Database connection: {'Available' if db else 'None'}")

        user = get_user_by_username(db, form_data.username)
        print(f"👤 User found in database: {'Yes' if user else 'No'}")

        # If database is not available or user not found, try mock users
        if not user:
            print("🔄 Trying mock users as fallback...")
            user = get_user_by_username(None, form_data.username)
            print(f"👤 Mock user found: {'Yes' if user else 'No'}")

        if user:
            print(f"🔑 User role: {user.get('role', 'Unknown')}")
            password_valid = verify_password(form_data.password, user['password_hash'])
            print(f"🔐 Password valid: {password_valid}")

        if not user or not verify_password(form_data.password, user['password_hash']):
            print("❌ Authentication failed - Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print("✅ Authentication successful")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['username']}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only administrators can create users")

    # Validate role
    if user.role not in ['admin', 'faculty', 'student']:
        raise HTTPException(status_code=400, detail="Invalid role. Must be admin, faculty, or student")

    db = next(get_db())
    if db is None:
        # For demo mode without database, simulate user creation
        return {
            "id": random.randint(100, 999),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "created_at": datetime.now()
        }
    
    cursor = db.cursor()

    # Check if user already exists
    cursor.execute("SELECT id FROM Users WHERE username = %s OR email = %s",
                  (user.username, user.email))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Create new user
    hashed_password = get_password_hash(user.password)
    cursor.execute(
        "INSERT INTO Users (username, email, password_hash, role, full_name) VALUES (%s, %s, %s, %s, %s)",
        (user.username, user.email, hashed_password, user.role, user.full_name)
    )
    db.commit()

    # Return created user
    user_id = cursor.lastrowid
    cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
    new_user = cursor.fetchone()
    return new_user

@app.put("/users/change-password")
async def change_password(password_data: PasswordChange, current_user: dict = Depends(get_current_user)):
    # Verify current password
    if not verify_password(password_data.current_password, current_user['password_hash']):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password
    if len(password_data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")
    
    db = next(get_db())
    if db is None:
        # For demo mode without database, simulate password change
        # In a real application, this would update the database
        # For now, we'll just return success since we're using mock data
        return {"message": "Password changed successfully (Demo mode - database not connected)"}
    
    cursor = db.cursor()
    
    # Update password
    new_password_hash = get_password_hash(password_data.new_password)
    cursor.execute(
        "UPDATE Users SET password_hash = %s WHERE id = %s",
        (new_password_hash, current_user['id'])
    )
    db.commit()
    
    return {"message": "Password changed successfully"}

@app.get("/users/", response_model=List[User])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only administrators can view all users")
    
    db = next(get_db())
    if db is None:
        # Mock data when database is not available
        return [
            {"id": 1, "username": "admin1", "email": "admin@university.edu", "role": "admin", "full_name": "S.M.Poobalan", "created_at": datetime.now()},
            {"id": 2, "username": "faculty1", "email": "prof.smith@university.edu", "role": "faculty", "full_name": "Prof. John Smith", "created_at": datetime.now()},
            {"id": 3, "username": "student1", "email": "student1@university.edu", "role": "student", "full_name": "John Doe", "created_at": datetime.now()}
        ]
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role, full_name, created_at FROM Users ORDER BY role, full_name")
    return cursor.fetchall()

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only administrators can delete users")
    
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    db = next(get_db())
    if db is None:
        # For demo mode without database, simulate user deletion
        return {"message": "User deleted successfully (Demo mode - database not connected)"}
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
    db.commit()
    
    return {"message": "User deleted successfully"}

# Test endpoint to check database
@app.get("/test/db")
async def test_database():
    try:
        db = next(get_db())
        if db is None:
            return {"status": "error", "message": "No database connection"}
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT username, role FROM Users LIMIT 3")
        users = cursor.fetchall()
        
        return {
            "status": "success", 
            "message": "Database connected",
            "users": users
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# User endpoints
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Classroom endpoints
@app.get("/classrooms/", response_model=List[Classroom])
async def get_classrooms(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    if db is None:
        # Mock data when database is not available
        return [
            {"id": 1, "name": "Room 101", "capacity": 30, "building": "Main Building", "floor": 1, "has_projector": True, "has_computer": True, "created_at": datetime.now()},
            {"id": 2, "name": "Room 102", "capacity": 25, "building": "Main Building", "floor": 1, "has_projector": False, "has_computer": False, "created_at": datetime.now()},
            {"id": 3, "name": "Lab 301", "capacity": 20, "building": "Lab Building", "floor": 3, "has_projector": True, "has_computer": True, "created_at": datetime.now()}
        ]
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Classrooms ORDER BY name")
    return cursor.fetchall()

@app.post("/classrooms/", response_model=Classroom)
async def create_classroom(classroom: ClassroomBase, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to create classrooms")

    db = next(get_db())
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Classrooms (name, capacity, building, floor, has_projector, has_computer) VALUES (%s, %s, %s, %s, %s, %s)",
        (classroom.name, classroom.capacity, classroom.building, classroom.floor,
         classroom.has_projector, classroom.has_computer)
    )
    db.commit()

    classroom_id = cursor.lastrowid
    cursor.execute("SELECT * FROM Classrooms WHERE id = %s", (classroom_id,))
    return cursor.fetchone()

@app.delete("/classrooms/{classroom_id}")
async def delete_classroom(classroom_id: int, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to delete classrooms")

    db = next(get_db())
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Classrooms WHERE id = %s", (classroom_id,))
    classroom = cursor.fetchone()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    cursor.execute("DELETE FROM Classrooms WHERE id = %s", (classroom_id,))
    db.commit()
    
    return {"message": "Classroom deleted successfully"}

# Faculty endpoints
@app.get("/faculty/", response_model=List[Faculty])
async def get_faculty(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    if db is None:
        # Mock data when database is not available
        return [
            {"id": 1, "name": "Prof. John Smith", "email": "prof.smith@university.edu", "department": "Computer Science", "phone": "+1234567890", "max_hours_per_day": 8, "max_hours_per_week": 40, "created_at": datetime.now()},
            {"id": 2, "name": "Dr. Emily Brown", "email": "dr.brown@university.edu", "department": "Mathematics", "phone": "+1234567891", "max_hours_per_day": 6, "max_hours_per_week": 30, "created_at": datetime.now()}
        ]
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Faculty ORDER BY name")
    return cursor.fetchall()

@app.post("/faculty/", response_model=Faculty)
async def create_faculty(faculty: FacultyBase, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to create faculty")

    db = next(get_db())
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Faculty (name, email, department, phone, max_hours_per_day, max_hours_per_week) VALUES (%s, %s, %s, %s, %s, %s)",
        (faculty.name, faculty.email, faculty.department, faculty.phone,
         faculty.max_hours_per_day, faculty.max_hours_per_week)
    )
    db.commit()

    faculty_id = cursor.lastrowid
    cursor.execute("SELECT * FROM Faculty WHERE id = %s", (faculty_id,))
    return cursor.fetchone()

@app.delete("/faculty/{faculty_id}")
async def delete_faculty(faculty_id: int, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to delete faculty")

    db = next(get_db())
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Faculty WHERE id = %s", (faculty_id,))
    faculty = cursor.fetchone()
    
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    cursor.execute("DELETE FROM Faculty WHERE id = %s", (faculty_id,))
    db.commit()
    
    return {"message": "Faculty deleted successfully"}

# Subject endpoints
@app.get("/subjects/", response_model=List[Subject])
async def get_subjects(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    if db is None:
        # Mock data when database is not available
        return [
            {"id": 1, "code": "CS101", "name": "Introduction to Programming", "department": "Computer Science", "credit_hours": 3, "semester": 1, "year": 2024, "is_lab": False, "requires_special_equipment": False, "created_at": datetime.now()},
            {"id": 2, "code": "MATH101", "name": "Calculus I", "department": "Mathematics", "credit_hours": 4, "semester": 1, "year": 2024, "is_lab": False, "requires_special_equipment": False, "created_at": datetime.now()},
            {"id": 3, "code": "CS201", "name": "Data Structures", "department": "Computer Science", "credit_hours": 4, "semester": 3, "year": 2024, "is_lab": True, "requires_special_equipment": True, "created_at": datetime.now()}
        ]
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Subjects ORDER BY code")
    return cursor.fetchall()

@app.post("/subjects/", response_model=Subject)
async def create_subject(subject: SubjectBase, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to create subjects")

    db = next(get_db())
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Subjects (code, name, department, credit_hours, semester, year, is_lab, requires_special_equipment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (subject.code, subject.name, subject.department, subject.credit_hours,
         subject.semester, subject.year, subject.is_lab, subject.requires_special_equipment)
    )
    db.commit()

    subject_id = cursor.lastrowid
    cursor.execute("SELECT * FROM Subjects WHERE id = %s", (subject_id,))
    return cursor.fetchone()

@app.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: int, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to delete subjects")

    db = next(get_db())
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Subjects WHERE id = %s", (subject_id,))
    subject = cursor.fetchone()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    cursor.execute("DELETE FROM Subjects WHERE id = %s", (subject_id,))
    db.commit()
    
    return {"message": "Subject deleted successfully"}

# Timetable endpoints
@app.get("/timetables/", response_model=List[Timetable])
async def get_timetables(current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    if db is None:
        # Mock data when database is not available
        return [
            {"id": 1, "name": "Fall 2024 Draft", "academic_year": "2024-2025", "semester": "fall", "status": "draft", "created_by": 1, "created_at": datetime.now(), "approved_at": None, "locked_at": None}
        ]
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Timetables ORDER BY created_at DESC")
    return cursor.fetchall()

@app.post("/timetables/", response_model=Timetable)
async def create_timetable(timetable: TimetableBase, current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Timetables (name, academic_year, semester, created_by) VALUES (%s, %s, %s, %s)",
        (timetable.name, timetable.academic_year, timetable.semester, current_user['id'])
    )
    db.commit()

    timetable_id = cursor.lastrowid
    cursor.execute("SELECT * FROM Timetables WHERE id = %s", (timetable_id,))
    return cursor.fetchone()

@app.delete("/timetables/{timetable_id}")
async def delete_timetable(timetable_id: int, current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Timetables WHERE id = %s", (timetable_id,))
    timetable = cursor.fetchone()
    
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    # Check if user has permission to delete
    if current_user['role'] != 'admin' and timetable[4] != current_user['id']:  # created_by field
        raise HTTPException(status_code=403, detail="Not authorized to delete this timetable")
    
    cursor.execute("DELETE FROM Timetables WHERE id = %s", (timetable_id,))
    db.commit()
    
    return {"message": "Timetable deleted successfully"}

# Caching for better performance
@lru_cache(maxsize=100)
def get_cached_faculty_assignments(subject_ids_tuple):
    """Cache faculty assignments for subjects"""
    return {}  # Mock implementation

# Schedule generation endpoint with improved efficiency
@app.post("/generate-schedule/", response_model=List[TimetableOption])
async def generate_schedule(request: ScheduleRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate optimized timetable using an improved constraint satisfaction approach
    """
    db = next(get_db())

    if db is None:
        # Use mock data for demo
        subjects = [
            {"id": 1, "code": "CS101", "name": "Introduction to Programming", "department": "Computer Science", "credit_hours": 3, "semester": 1, "year": 2024, "is_lab": False, "requires_special_equipment": False},
            {"id": 2, "code": "MATH101", "name": "Calculus I", "department": "Mathematics", "credit_hours": 4, "semester": 1, "year": 2024, "is_lab": False, "requires_special_equipment": False},
            {"id": 3, "code": "CS201", "name": "Data Structures", "department": "Computer Science", "credit_hours": 4, "semester": 3, "year": 2024, "is_lab": True, "requires_special_equipment": True}
        ]
        faculty = [
            {"id": 1, "name": "Prof. John Smith", "department": "Computer Science", "max_hours_per_day": 8, "max_hours_per_week": 40},
            {"id": 2, "name": "Dr. Emily Brown", "department": "Mathematics", "max_hours_per_day": 6, "max_hours_per_week": 30}
        ]
        classrooms = [
            {"id": 1, "name": "Room 101", "capacity": 30, "has_projector": True, "has_computer": True},
            {"id": 2, "name": "Room 102", "capacity": 25, "has_projector": False, "has_computer": False},
            {"id": 3, "name": "Lab 301", "capacity": 20, "has_projector": True, "has_computer": True}
        ]
    else:
        # Get data from database
        cursor = db.cursor(dictionary=True)
        
        # Use parameterized query for security
        placeholders = ','.join(['%s'] * len(request.subjects))
        cursor.execute(f"SELECT * FROM Subjects WHERE id IN ({placeholders})", request.subjects)
        subjects = cursor.fetchall()

        cursor.execute("SELECT * FROM Faculty")
        faculty = cursor.fetchall()

        cursor.execute("SELECT * FROM Classrooms")
        classrooms = cursor.fetchall()

    # Generate multiple timetable options concurrently for better performance
    tasks = []
    for attempt in range(3):
        task = asyncio.create_task(
            generate_timetable_option_async(subjects, faculty, classrooms, request.constraints, attempt + 1)
        )
        tasks.append(task)
    
    options = await asyncio.gather(*tasks)
    return options

async def generate_timetable_option_async(subjects, faculty, classrooms, constraints, option_id):
    """Generate a single timetable option asynchronously"""
    schedule = generate_timetable_option_optimized(subjects, faculty, classrooms, constraints)
    score = calculate_schedule_score_optimized(schedule, subjects, faculty, classrooms)
    conflicts = identify_conflicts_optimized(schedule, subjects, faculty, classrooms)

    return TimetableOption(
        id=option_id,
        name=f"Option {option_id}",
        schedule=schedule,
        score=score,
        conflicts=conflicts
    )

def generate_timetable_option_optimized(subjects, faculty, classrooms, constraints):
    """Optimized timetable generation with better algorithm"""
    schedule = []
    used_slots = set()  # Use set for O(1) lookup
    faculty_hours = {f['id']: {'daily': {}, 'weekly': 0} for f in faculty}
    
    # Pre-sort subjects by priority for better scheduling
    subjects_sorted = sorted(subjects, key=lambda x: (
        x.get('requires_special_equipment', False),
        -x.get('credit_hours', 0),
        x.get('is_lab', False)
    ), reverse=True)
    
    # Time slots optimization
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    time_slots = [(hour, hour + 1) for hour in range(8, 17)]  # 8 AM to 5 PM
    
    for subject in subjects_sorted:
        scheduled = False
        # Try to find the best slot using scoring
        best_slot = None
        best_score = -1
        
        for day in days:
            for start_hour, end_hour in time_slots:
                if end_hour - start_hour < subject.get('credit_hours', 1):
                    continue
                    
                # Find suitable faculty and classroom
                suitable_faculty = find_suitable_faculty_optimized(subject, faculty, day, start_hour, end_hour, used_slots, faculty_hours)
                suitable_classroom = find_suitable_classroom_optimized(subject, classrooms, day, start_hour, end_hour, used_slots)
                
                if suitable_faculty and suitable_classroom:
                    slot_score = calculate_slot_score(day, start_hour, subject, suitable_faculty, suitable_classroom)
                    if slot_score > best_score:
                        best_score = slot_score
                        best_slot = (day, start_hour, end_hour, suitable_faculty, suitable_classroom)
        
        # Schedule the subject in the best slot found
        if best_slot:
            day, start_hour, end_hour, faculty_member, classroom = best_slot
            entry = ScheduleEntryBase(
                subject_id=subject['id'],
                faculty_id=faculty_member['id'],
                classroom_id=classroom['id'],
                day_of_week=day,
                start_time=f"{start_hour:02d}:00:00",
                end_time=f"{end_hour:02d}:00:00"
            )
            schedule.append(entry)
            
            # Update tracking
            slot_key = (faculty_member['id'], classroom['id'], day, start_hour)
            used_slots.add(slot_key)
            
            # Update faculty hours
            if day not in faculty_hours[faculty_member['id']]['daily']:
                faculty_hours[faculty_member['id']]['daily'][day] = 0
            faculty_hours[faculty_member['id']]['daily'][day] += (end_hour - start_hour)
            faculty_hours[faculty_member['id']]['weekly'] += (end_hour - start_hour)
    
    return schedule

def find_suitable_faculty_optimized(subject, faculty, day, start_hour, end_hour, used_slots, faculty_hours):
    """Find suitable faculty with optimized checking"""
    for faculty_member in faculty:
        # Check if faculty is available
        slot_key = (faculty_member['id'], None, day, start_hour)  # None for classroom since we're checking faculty
        if any(key[0] == faculty_member['id'] and key[2] == day and key[3] == start_hour for key in used_slots):
            continue
            
        # Check daily and weekly hour limits
        daily_hours = faculty_hours[faculty_member['id']]['daily'].get(day, 0)
        weekly_hours = faculty_hours[faculty_member['id']]['weekly']
        
        if daily_hours + (end_hour - start_hour) > faculty_member.get('max_hours_per_day', 8):
            continue
        if weekly_hours + (end_hour - start_hour) > faculty_member.get('max_hours_per_week', 40):
            continue
            
        # Check department match (simplified)
        if subject.get('department') == faculty_member.get('department'):
            return faculty_member
    
    return None

def find_suitable_classroom_optimized(subject, classrooms, day, start_hour, end_hour, used_slots):
    """Find suitable classroom with optimized checking"""
    for classroom in classrooms:
        # Check if classroom is available
        if any(key[1] == classroom['id'] and key[2] == day and key[3] == start_hour for key in used_slots):
            continue
            
        # Check capacity (assume minimum 20 students)
        if classroom.get('capacity', 0) < 20:
            continue
            
        # Check special equipment requirements
        if subject.get('requires_special_equipment', False):
            if not (classroom.get('has_projector', False) or classroom.get('has_computer', False)):
                continue
                
        return classroom
    
    return None

def calculate_slot_score(day, start_hour, subject, faculty_member, classroom):
    """Calculate score for a time slot"""
    score = 100
    
    # Prefer morning slots
    if 9 <= start_hour <= 11:
        score += 20
    elif 14 <= start_hour <= 16:
        score += 10
    
    # Prefer mid-week days
    if day in ['tuesday', 'wednesday', 'thursday']:
        score += 15
    
    # Bonus for equipment match
    if subject.get('requires_special_equipment', False) and classroom.get('has_computer', False):
        score += 25
    
    # Bonus for department match
    if subject.get('department') == faculty_member.get('department'):
        score += 30
    
    return score

def calculate_schedule_score_optimized(schedule, subjects, faculty, classrooms):
    """Optimized schedule scoring"""
    if not schedule:
        return 0
        
    score = 100
    conflicts = identify_conflicts_optimized(schedule, subjects, faculty, classrooms)
    score -= len(conflicts) * 15  # Higher penalty for conflicts
    
    # Bonus for balanced distribution
    day_counts = {}
    for entry in schedule:
        day = entry.day_of_week
        day_counts[day] = day_counts.get(day, 0) + 1
    
    if len(day_counts) >= 4:  # Classes spread across at least 4 days
        score += 20
    
    # Bonus for optimal time usage
    time_efficiency = len(schedule) / max(len(subjects), 1) * 100
    score += min(time_efficiency, 50)
    
    return max(0, score)

def identify_conflicts_optimized(schedule, subjects, faculty, classrooms):
    """Optimized conflict detection using sets"""
    conflicts = []
    faculty_slots = set()
    classroom_slots = set()
    
    for entry in schedule:
        faculty_slot = (entry.faculty_id, entry.day_of_week, entry.start_time)
        classroom_slot = (entry.classroom_id, entry.day_of_week, entry.start_time)
        
        if faculty_slot in faculty_slots:
            conflicts.append(f"Faculty {entry.faculty_id} double-booked on {entry.day_of_week} at {entry.start_time}")
        else:
            faculty_slots.add(faculty_slot)
            
        if classroom_slot in classroom_slots:
            conflicts.append(f"Classroom {entry.classroom_id} double-booked on {entry.day_of_week} at {entry.start_time}")
        else:
            classroom_slots.add(classroom_slot)
    
    return conflicts

def generate_timetable_option(subjects, faculty, classrooms, constraints):
    """Generate a single timetable option using greedy algorithm"""
    schedule = []
    used_slots = {}  # Track used time slots per faculty and room

    # Time slots (Monday to Friday, 8 AM to 6 PM)
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    time_slots = []

    for hour in range(8, 18):
        time_slots.append(time(hour, 0))

    # Sort subjects by priority (credit hours, lab requirements)
    subjects.sort(key=lambda x: (x['requires_special_equipment'], -x['credit_hours']))

    for subject in subjects:
        # Find available faculty for this subject
        cursor = mysql.connector.connect(**DB_CONFIG).cursor(dictionary=True)
        cursor.execute("SELECT f.* FROM Faculty f JOIN FacultySubjectAssignments fsa ON f.id = fsa.faculty_id WHERE fsa.subject_id = %s", (subject['id'],))
        available_faculty = cursor.fetchall()

        if not available_faculty:
            continue

        # Try to schedule the subject
        scheduled = False
        for faculty_member in available_faculty:
            for day in days:
                for i in range(len(time_slots) - subject['credit_hours']):
                    start_time = time_slots[i]
                    end_time = time_slots[i + subject['credit_hours']]

                    # Check constraints
                    if can_schedule_subject(subject, faculty_member, day, start_time, end_time, used_slots, constraints):
                        # Find suitable classroom
                        classroom = find_suitable_classroom(subject, classrooms, day, start_time, end_time)
                        if classroom:
                            entry = ScheduleEntryBase(
                                subject_id=subject['id'],
                                faculty_id=faculty_member['id'],
                                classroom_id=classroom['id'],
                                day_of_week=day,
                                start_time=start_time.strftime('%H:%M:%S'),
                                end_time=end_time.strftime('%H:%M:%S')
                            )
                            schedule.append(entry)

                            # Update used slots
                            used_slots[(faculty_member['id'], day, start_time)] = end_time
                            used_slots[(classroom['id'], day, start_time)] = end_time
                            scheduled = True
                            break
                if scheduled:
                    break
            if scheduled:
                break

    return schedule

def can_schedule_subject(subject, faculty, day, start_time, end_time, used_slots, constraints):
    """Check if subject can be scheduled in given time slot"""
    # Check faculty availability
    faculty_key = (faculty['id'], day, start_time)
    if faculty_key in used_slots:
        return False

    # Check if faculty has reached daily limit
    daily_hours = sum(
        (datetime.combine(datetime.today(), end) - datetime.combine(datetime.today(), start)).seconds / 3600
        for (f_id, d, start), end_time in used_slots.items()
        if f_id == faculty['id'] and d == day
    )

    if daily_hours + (end_time.hour - start_time.hour) > faculty['max_hours_per_day']:
        return False

    # Check subject-specific constraints
    if subject['requires_special_equipment']:
        # Need lab with special equipment
        pass

    return True

def find_suitable_classroom(subject, classrooms, day, start_time, end_time):
    """Find suitable classroom for the subject"""
    for classroom in classrooms:
        # Check room availability
        room_key = (classroom['id'], day, start_time)
        if room_key in used_slots:
            continue

        # Check capacity
        if classroom['capacity'] < 30:  # Assume minimum class size
            continue

        # Check special requirements
        if subject['requires_special_equipment'] and not (classroom['has_projector'] or classroom['has_computer']):
            continue

        return classroom
    return None

def calculate_schedule_score(schedule, subjects, faculty, classrooms):
    """Calculate a score for the schedule quality"""
    score = 100

    # Penalty for conflicts
    conflicts = identify_conflicts(schedule, subjects, faculty, classrooms)
    score -= len(conflicts) * 10

    # Bonus for optimal time distribution
    day_distribution = {}
    for entry in schedule:
        day = entry['day_of_week']
        day_distribution[day] = day_distribution.get(day, 0) + 1

    # Prefer balanced distribution across days
    if len(day_distribution) == 5:  # All weekdays used
        score += 10

    return max(0, score)

def identify_conflicts(schedule, subjects, faculty, classrooms):
    """Identify conflicts in the schedule"""
    conflicts = []

    # Check for double-booked faculty
    faculty_schedule = {}
    for entry in schedule:
        key = (entry['faculty_id'], entry['day_of_week'], entry['start_time'])
        if key in faculty_schedule:
            conflicts.append(f"Faculty {entry['faculty_id']} double-booked at {entry['start_time']}")
        faculty_schedule[key] = entry['end_time']

    # Check for double-booked rooms
    room_schedule = {}
    for entry in schedule:
        key = (entry['classroom_id'], entry['day_of_week'], entry['start_time'])
        if key in room_schedule:
            conflicts.append(f"Room {entry['classroom_id']} double-booked at {entry['start_time']}")
        room_schedule[key] = entry['end_time']

    return conflicts

# Export endpoints
@app.get("/export/timetable/{timetable_id}")
async def export_timetable(timetable_id: int, format: str = "json", current_user: dict = Depends(get_current_user)):
    db = next(get_db())
    cursor = db.cursor(dictionary=True)

    # Get timetable
    cursor.execute("SELECT * FROM Timetables WHERE id = %s", (timetable_id,))
    timetable = cursor.fetchone()
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")

    # Get schedule entries
    cursor.execute("SELECT * FROM ScheduleEntries WHERE timetable_id = %s", (timetable_id,))
    schedule = cursor.fetchall()

    if format == "csv":
        # Export as CSV
        csv_data = "Subject,Faculty,Room,Day,Start Time,End Time\n"
        for entry in schedule:
            csv_data += f"{entry['subject_id']},{entry['faculty_id']},{entry['classroom_id']},{entry['day_of_week']},{entry['start_time']},{entry['end_time']}\n"
        return {"data": csv_data, "filename": f"timetable_{timetable_id}.csv"}

    # Default JSON export
    return {
        "timetable": timetable,
        "schedule": schedule
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
