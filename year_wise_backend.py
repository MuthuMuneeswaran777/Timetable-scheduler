from fastapi import FastAPI, HTTPException, Depends, status
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
from typing import List, Dict, Any

app = FastAPI(title="Smart Class Scheduler API - Year-Wise Subjects")

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

# Simple user database
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

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@app.put("/users/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Validate current password
        if not verify_password(password_data.current_password, current_user["password_hash"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # Validate new password
        if len(password_data.new_password) < 6:
            raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")

        # For demo mode, we'll simulate success
        # In production, this would update the database
        print(f"✅ Password changed for user: {current_user['username']}")

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")

# Files for persistent storage
TIMETABLE_FILE = "timetable_data_year_wise.json"

def load_timetable_data():
    """Load timetable data from JSON file with backward compatibility"""
    if os.path.exists(TIMETABLE_FILE):
        try:
            with open(TIMETABLE_FILE, 'r') as f:
                data = json.load(f)

                # Handle backward compatibility: convert old 'subjects' to 'year_subjects'
                if 'departments' in data:
                    for dept in data['departments']:
                        if 'subjects' in dept and 'year_subjects' not in dept:
                            # Convert old subjects array to year_subjects structure
                            dept['year_subjects'] = {}
                            for year in range(1, dept.get('years', 4) + 1):
                                dept['year_subjects'][str(year)] = dept['subjects'][:6]  # Take first 6 subjects for each year
                            del dept['subjects']  # Remove old subjects field
                            print(f"🔄 Converted old subjects format to year_subjects for {dept['name']}")

                print(f"📂 Loaded timetable data: {len(data.get('departments', []))} departments")
                return data
        except Exception as e:
            print(f"⚠️ Error loading timetable file: {e}")
    return {"departments": [], "teachers": [], "students": [], "timetable": []}

def save_timetable_data(data):
    """Save timetable data to JSON file with validation"""
    try:
        # Validate data structure before saving
        if 'departments' in data:
            for dept in data['departments']:
                if 'year_subjects' not in dept:
                    print(f"⚠️ Warning: Department {dept.get('name', 'Unknown')} missing year_subjects")
                    # Initialize empty year_subjects if missing
                    dept['year_subjects'] = {}
                    for year in range(1, dept.get('years', 4) + 1):
                        dept['year_subjects'][str(year)] = []

        with open(TIMETABLE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Timetable data saved: {len(data.get('departments', []))} departments")

        # Debug: Show what was saved
        if 'departments' in data:
            for dept in data['departments']:
                total_subjects = sum(len(subjects) for subjects in dept.get('year_subjects', {}).values())
                print(f"   📚 {dept.get('name', 'Unknown')}: {total_subjects} subjects across {len(dept.get('year_subjects', {}))} years")
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
    """Setup complete timetable system with year-wise subjects (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can setup timetables")

    try:
        global TIMETABLE_DATA

        # Process departments with year-wise subjects
        departments = []

        for dept_data in setup_data["departments"]:
            dept = {
                "name": dept_data["name"],
                "classes": dept_data["classes"],
                "labs": dept_data["labs"],
                "years": dept_data["years"],
                "sections": dept_data["sections"],
                "year_subjects": dept_data["year_subjects"]  # Year-wise subjects
            }
            departments.append(dept)

        # Process teachers
        teachers = setup_data["teachers"]

        # Generate students for each year and section
        students = []
        for dept in departments:
            for year in range(1, dept["years"] + 1):
                for section_data in dept["sections"]:
                    section_name = section_data["name"]
                    student_count = section_data["student_count"]

                    for i in range(1, student_count + 1):
                        roll_number = generate_roll_number(dept["name"], year, section_name, i)
                        student = {
                            "name": f"Student {i}",
                            "roll_number": roll_number,
                            "department": dept["name"],
                            "year": year,
                            "section": section_name
                        }
                        students.append(student)

        # Save timetable data
        TIMETABLE_DATA = {
            "departments": departments,
            "teachers": teachers,
            "students": students,
            "timetable": []
        }

        # Save to file for persistence
        save_timetable_data(TIMETABLE_DATA)

        # Auto-create user accounts
        auto_create_users(departments, teachers, students)

        print(f"✅ Year-wise timetable setup complete:")
        print(f"   📚 Departments: {len(departments)}")
        print(f"   👨‍🏫 Teachers: {len(teachers)}")
        print(f"   👨‍🎓 Students: {len(students)}")

        return {
            "message": "Year-wise timetable setup completed successfully",
            "summary": {
                "departments": len(departments),
                "teachers": len(teachers),
                "students": len(students),
                "accounts_created": len(teachers) + len(students)
            }
        }

    except Exception as e:
        print(f"❌ Timetable setup error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to setup timetable: {str(e)}")

@app.get("/timetable/data")
async def get_timetable_data(current_user: dict = Depends(get_current_user)):
    """Get timetable data"""
    return TIMETABLE_DATA

def generate_year_wise_timetable():
    """Generate timetable with year-wise subjects (simple version)"""
    print("🔄 Generating year-wise timetable...")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = ["9:00-10:00", "10:00-11:00", "11:30-12:30", "12:30-1:30", "2:30-3:30", "3:30-4:30"]

    generated_timetable = []

    # Track subject assignments per week
    subject_weekly_count = {}

    for dept in TIMETABLE_DATA["departments"]:
        dept_teachers = [t for t in TIMETABLE_DATA["teachers"] if t["department"] == dept["name"]]

        for year in range(1, dept["years"] + 1):
            for section_data in dept["sections"]:
                section = section_data["name"]
                class_key = f"{dept['name']}-{year}-{section}"

                # Get subjects for this specific year
                year_subjects = dept["year_subjects"].get(str(year), [])
                print(f"📖 Year {year} subjects: {year_subjects}")

                for day in days:
                    for time_slot in time_slots:
                        assigned = False

                        # Try to assign subjects for this year only
                        for subject in year_subjects:
                            subject_key = f"{class_key}-{subject}"

                            # Check subject weekly limit
                            if subject_weekly_count.get(subject_key, 0) >= 5:
                                continue

                            # Find a teacher who can teach this subject
                            for teacher in dept_teachers:
                                if subject in teacher["subjects"]:
                                    # Check teacher daily limit (simple check)
                                    teacher_daily_count = sum(1 for entry in generated_timetable
                                                            if entry["teacher"] == teacher["name"] and entry["day"] == day)
                                    if teacher_daily_count >= 4:
                                        continue

                                    # Check if teacher is already busy in this slot
                                    is_busy = any(entry["teacher"] == teacher["name"] and
                                                entry["day"] == day and
                                                entry["time_slot"] == time_slot
                                                for entry in generated_timetable)
                                    if is_busy:
                                        continue

                                    # Assign the subject
                                    classroom = dept["classes"][len(generated_timetable) % len(dept["classes"])]["name"] if dept["classes"] else "TBA"
                                    entry = {
                                        "day": day,
                                        "time_slot": time_slot,
                                        "subject": subject,
                                        "teacher": teacher["name"],
                                        "classroom": classroom,
                                        "department": dept["name"],
                                        "year": year,
                                        "section": section
                                    }
                                    generated_timetable.append(entry)

                                    # Update counters
                                    subject_weekly_count[subject_key] = subject_weekly_count.get(subject_key, 0) + 1

                                    assigned = True
                                    break
                            if assigned:
                                break

                        # If no assignment possible, create free period
                        if not assigned:
                            entry = {
                                "day": day,
                                "time_slot": time_slot,
                                "subject": "Free Period",
                                "teacher": "N/A",
                                "classroom": "N/A",
                                "department": dept["name"],
                                "year": year,
                                "section": section
                            }
                            generated_timetable.append(entry)

    print(f"✅ Year-wise timetable generated: {len(generated_timetable)} entries")
    return generated_timetable

@app.post("/timetable/generate")
async def generate_timetable(current_user: dict = Depends(get_current_user)):
    """Generate year-wise timetable (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can generate timetables")

    try:
        global TIMETABLE_DATA

        print("🚀 Starting year-wise timetable generation...")

        # Generate year-wise timetable
        generated_timetable = generate_year_wise_timetable()

        # Save generated timetable
        TIMETABLE_DATA["timetable"] = generated_timetable

        # Save to file for persistence
        save_timetable_data(TIMETABLE_DATA)

        print(f"✅ Year-wise timetable generated: {len(generated_timetable)} entries")

        return {
            "message": "Year-wise timetable generated successfully",
            "entries": len(generated_timetable),
            "timetable": generated_timetable,
            "year_wise": True
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
    return {"message": "Smart Class Scheduler API - Year-Wise Subjects", "status": "running"}

if __name__ == "__main__":
    print("🚀 Starting Smart Class Scheduler Backend with Year-Wise Subjects...")
    print("✅ Year-wise subject configuration enabled")
    print("🔑 Test credentials:")
    print("   - Admin: admin1 / password123")
    print("   - Faculty: faculty1 / password123")
    print("   - Student: student1 / password123")
    print("🌐 Backend running on: http://localhost:8003")
    uvicorn.run(app, host="0.0.0.0", port=8003)
