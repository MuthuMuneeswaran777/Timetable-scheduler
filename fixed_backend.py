from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import secrets
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uvicorn
import json
import os

app = FastAPI(title="Smart Class Scheduler API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-change-in-production-12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simple password hashing without bcrypt
def hash_password(password: str) -> str:
    """Simple password hashing using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, password_hash = hashed_password.split(":")
        return hashlib.sha256((plain_password + salt).encode()).hexdigest() == password_hash
    except:
        return False

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    full_name: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str

# Simple user database - this works without MySQL or bcrypt
USERS_DB = {
    "admin1": {
        "id": 1,
        "username": "admin1",
        "email": "admin@university.edu",
        "password_hash": hash_password("password123"),
        "role": "admin",
        "full_name": "S.M.Poobalan"
    },
    "faculty1": {
        "id": 2,
        "username": "faculty1",
        "email": "faculty@university.edu",
        "password_hash": hash_password("password123"),
        "role": "faculty",
        "full_name": "Prof. John Smith"
    },
    "student1": {
        "id": 3,
        "username": "student1",
        "email": "student@university.edu",
        "password_hash": hash_password("password123"),
        "role": "student",
        "full_name": "John Doe"
    }
}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str):
    return USERS_DB.get(username)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"🔐 Login attempt: {form_data.username}")
    user = get_user(form_data.username)
    if not user:
        print(f"❌ User not found: {form_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user["password_hash"]):
        print(f"❌ Invalid password for: {form_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ Login successful: {form_data.username}")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.put("/users/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        print(f"🔐 Password change request for: {current_user['username']}")
        
        # Verify current password
        if not verify_password(request.current_password, current_user["password_hash"]):
            print(f"❌ Invalid current password for: {current_user['username']}")
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password in memory database
        new_password_hash = hash_password(request.new_password)
        USERS_DB[current_user["username"]]["password_hash"] = new_password_hash
        
        print(f"✅ Password changed successfully for: {current_user['username']}")
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Password change error: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

@app.post("/users/")
async def create_user(
    request: UserCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can create users")
    
    if request.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Generate new user ID safely
    if not USERS_DB:
        new_id = 1
    else:
        new_id = max([user["id"] for user in USERS_DB.values()]) + 1
    
    # Create new user
    USERS_DB[request.username] = {
        "id": new_id,
        "username": request.username,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "role": request.role,
        "full_name": request.full_name
    }
    
    print(f"✅ User created: {request.username} ({request.role})")
    return {
        "id": new_id,
        "username": request.username,
        "email": request.email,
        "role": request.role,
        "full_name": request.full_name
    }

@app.get("/users/")
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can view users")
    
    return [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"]
        }
        for user in USERS_DB.values()
    ]

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Delete user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete users")
    
    # Find user by ID
    user_to_delete = None
    username_to_delete = None
    for username, user in USERS_DB.items():
        if user["id"] == user_id:
            user_to_delete = user
            username_to_delete = username
            break
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_to_delete["id"] == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Delete user
    del USERS_DB[username_to_delete]
    print(f"✅ User deleted: {username_to_delete}")
    return {"message": "User deleted successfully"}

# Files for persistent storage
TIMETABLE_FILE = "timetable_data.json"

def load_timetable_data():
    """Load timetable data from JSON file"""
    if os.path.exists(TIMETABLE_FILE):
        try:
            with open(TIMETABLE_FILE, 'r') as f:
                data = json.load(f)
                print(f"📂 Loaded timetable data: {len(data.get('departments', []))} departments, {len(data.get('teachers', []))} teachers, {len(data.get('students', []))} students")
                return data
        except Exception as e:
            print(f"⚠️ Error loading timetable file: {e}")
    return {"departments": [], "teachers": [], "students": [], "timetable": []}

def save_timetable_data(data):
    """Save timetable data to JSON file"""
    try:
        with open(TIMETABLE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Timetable data saved: {len(data.get('departments', []))} departments, {len(data.get('teachers', []))} teachers, {len(data.get('students', []))} students")
    except Exception as e:
        print(f"❌ Error saving timetable data: {e}")

# Load timetable data at startup
TIMETABLE_DATA = load_timetable_data()

def generate_roll_number(department: str, year: int, section: str, student_count: int):
    """Generate roll number in format: DEPT-YEAR-SECTION-NUMBER"""
    dept_code = department[:3].upper()
    return f"{dept_code}{year}{section}{student_count:03d}"

def auto_create_users(departments_data, teachers_data, students_data):
    """Automatically create user accounts for teachers and students"""
    global USERS_DB
    
    # Get current max ID safely
    def get_next_id():
        if not USERS_DB:
            return 1
        return max([user["id"] for user in USERS_DB.values()]) + 1
    
    # Create teacher accounts
    for teacher in teachers_data:
        username = teacher["employee_id"]
        if username not in USERS_DB:
            new_id = get_next_id()
            USERS_DB[username] = {
                "id": new_id,
                "username": username,
                "email": f"{username}@university.edu",
                "password_hash": hash_password(username),  # Default password is employee_id
                "role": "faculty",
                "full_name": teacher["name"]
            }
            print(f"✅ Created faculty account: {username}")
    
    # Create student accounts
    for student in students_data:
        username = student["roll_number"]
        if username not in USERS_DB:
            new_id = get_next_id()
            USERS_DB[username] = {
                "id": new_id,
                "username": username,
                "email": f"{username}@university.edu",
                "password_hash": hash_password(username),  # Default password is roll_number
                "role": "student",
                "full_name": student["name"]
            }
            print(f"✅ Created student account: {username}")

# Timetable Management Endpoints
@app.post("/timetable/setup")
async def setup_timetable(
    setup_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Setup complete timetable system (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can setup timetables")
    
    try:
        global TIMETABLE_DATA
        
        # Process departments and generate students
        departments = []
        all_teachers = []
        all_students = []
        
        for dept_data in setup_data["departments"]:
            dept = {
                "name": dept_data["name"],
                "classes": dept_data["classes"],
                "labs": dept_data["labs"],
                "years": dept_data["years"],
                "sections": dept_data["sections"],
                "subjects": dept_data["subjects"]
            }
            departments.append(dept)
            
            # Generate students for each year and section
            for year in range(1, dept_data["years"] + 1):
                for section_data in dept_data["sections"]:
                    section_name = section_data["name"]
                    student_count = section_data["student_count"]
                    
                    for i in range(1, student_count + 1):
                        roll_number = generate_roll_number(dept_data["name"], year, section_name, i)
                        student = {
                            "name": f"Student {i}",
                            "roll_number": roll_number,
                            "department": dept_data["name"],
                            "year": year,
                            "section": section_name
                        }
                        all_students.append(student)
        
        # Process teachers
        for teacher_data in setup_data["teachers"]:
            teacher = {
                "name": teacher_data["name"],
                "employee_id": teacher_data["employee_id"],
                "subjects": teacher_data["subjects"],
                "department": teacher_data["department"]
            }
            all_teachers.append(teacher)
        
        # Save timetable data
        TIMETABLE_DATA = {
            "departments": departments,
            "teachers": all_teachers,
            "students": all_students,
            "timetable": []
        }
        
        # Save to file for persistence
        save_timetable_data(TIMETABLE_DATA)
        
        # Auto-create user accounts
        auto_create_users(departments, all_teachers, all_students)
        
        print(f"✅ Timetable setup complete:")
        print(f"   📚 Departments: {len(departments)}")
        print(f"   👨‍🏫 Teachers: {len(all_teachers)}")
        print(f"   👨‍🎓 Students: {len(all_students)}")
        
        return {
            "message": "Timetable setup completed successfully",
            "summary": {
                "departments": len(departments),
                "teachers": len(all_teachers),
                "students": len(all_students),
                "accounts_created": len(all_teachers) + len(all_students)
            }
        }
        
    except Exception as e:
        print(f"❌ Timetable setup error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to setup timetable: {str(e)}")

@app.get("/timetable/data")
async def get_timetable_data(current_user: dict = Depends(get_current_user)):
    """Get timetable data"""
    return TIMETABLE_DATA

@app.post("/timetable/generate")
async def generate_timetable(current_user: dict = Depends(get_current_user)):
    """Generate automatic timetable with constraints (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can generate timetables")

    try:
        global TIMETABLE_DATA
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        time_slots = ["9:00-10:00", "10:00-11:00", "11:30-12:30", "12:30-1:30", "2:30-3:30", "3:30-4:30"]

        generated_timetable = []
        subject_weekly_count = {}

        for dept in TIMETABLE_DATA["departments"]:
            print(f"\nProcessing Department: {dept['name']}")
            dept_teachers = [t for t in TIMETABLE_DATA["teachers"] if t["department"] == dept["name"]]

            for year in range(1, dept["years"] + 1):
                for section_data in dept["sections"]:
                    section = section_data["name"]
                    class_key = f"{dept['name']}-{year}-{section}"
                    print(f"  Processing Class: {class_key}")
                    teacher_daily_count = {day: {} for day in days}

                    for day in days:
                        for time_slot in time_slots:
                            assigned = False
                            for subject in dept["subjects"]:
                                subject_key = f"{class_key}-{subject}"
                                
                                if subject_weekly_count.get(subject_key, 0) >= 5:
                                    print(f"    - Slot {day} {time_slot}: Subject {subject} limit reached")
                                    continue

                                for t in dept_teachers:
                                    if subject in t["subjects"]:
                                        teacher_name = t["name"]
                                        
                                        if teacher_daily_count[day].get(teacher_name, 0) >= 4:
                                            print(f"    - Slot {day} {time_slot}: Teacher {teacher_name} daily limit reached")
                                            continue

                                        is_busy = any(
                                            e["teacher"] == teacher_name and e["day"] == day and e["time_slot"] == time_slot
                                            for e in generated_timetable
                                        )
                                        if is_busy:
                                            print(f"    - Slot {day} {time_slot}: Teacher {teacher_name} is busy")
                                            continue

                                        classroom = dept["classes"][len(generated_timetable) % len(dept["classes"])]["name"] if dept["classes"] else "TBA"
                                        entry = {
                                            "day": day, "time_slot": time_slot, "subject": subject,
                                            "teacher": teacher_name, "classroom": classroom, "department": dept["name"],
                                            "year": year, "section": section
                                        }
                                        generated_timetable.append(entry)

                                        subject_weekly_count[subject_key] = subject_weekly_count.get(subject_key, 0) + 1
                                        teacher_daily_count[day][teacher_name] = teacher_daily_count[day].get(teacher_name, 0) + 1
                                        
                                        print(f"    - Slot {day} {time_slot}: Assigned {subject} to {teacher_name}")
                                        assigned = True
                                        break
                                if assigned:
                                    break

                            if not assigned:
                                print(f"    - Slot {day} {time_slot}: No valid assignment found, creating Free Period")
                                entry = {
                                    "day": day, "time_slot": time_slot, "subject": "Free Period",
                                    "teacher": "N/A", "classroom": "N/A", "department": dept["name"],
                                    "year": year, "section": section
                                }
                                generated_timetable.append(entry)

        TIMETABLE_DATA["timetable"] = generated_timetable
        save_timetable_data(TIMETABLE_DATA)
        print(f"✅ Timetable generated with constraints: {len(generated_timetable)} entries")

        return {
            "message": "Timetable generated successfully with constraints",
            "entries": len(generated_timetable),
            "timetable": generated_timetable
        }

        
    except Exception as e:
        print(f"❌ Timetable generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate timetable: {str(e)}")

@app.get("/timetable/view")
async def view_timetable(
    department: str = None,
    year: int = None,
    section: str = None,
    current_user: dict = Depends(get_current_user)
):
    """View timetable with filters"""
    timetable = TIMETABLE_DATA["timetable"]
    
    # Apply filters
    if department:
        timetable = [entry for entry in timetable if entry["department"] == department]
    if year:
        timetable = [entry for entry in timetable if entry["year"] == year]
    if section:
        timetable = [entry for entry in timetable if entry["section"] == section]
    
    # For students, filter by their department/year/section
    if current_user["role"] == "student":
        # Extract student info from roll number or user data
        student_data = next((s for s in TIMETABLE_DATA["students"] if s["roll_number"] == current_user["username"]), None)
        if student_data:
            timetable = [entry for entry in timetable 
                        if entry["department"] == student_data["department"] 
                        and entry["year"] == student_data["year"]
                        and entry["section"] == student_data["section"]]
    
    return {"timetable": timetable}

@app.get("/test/auth")
async def test_auth():
    return {"status": "success", "message": "Authentication system working!"}

@app.get("/")
async def root():
    return {"message": "Smart Class Scheduler API", "status": "running"}

if __name__ == "__main__":
    print("🚀 Starting Smart Class Scheduler Backend...")
    print("✅ Simple authentication system loaded (No bcrypt dependency)")
    print("🔑 Test credentials:")
    print("   - Admin: admin1 / password123")
    print("   - Faculty: faculty1 / password123") 
    print("   - Student: student1 / password123")
    print("🌐 Backend running on: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
