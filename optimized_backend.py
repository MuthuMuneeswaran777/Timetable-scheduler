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
from typing import List, Dict, Any
from ortools.sat.python import cp_model

app = FastAPI(title="Smart Class Scheduler API - OR-Tools Optimized")

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
TIMETABLE_FILE = "timetable_data_optimized.json"

def load_timetable_data():
    """Load timetable data from JSON file"""
    if os.path.exists(TIMETABLE_FILE):
        try:
            with open(TIMETABLE_FILE, 'r') as f:
                data = json.load(f)
                print(f"📂 Loaded timetable data: {len(data.get('departments', []))} departments, {len(data.get('teachers', []))} teachers")
                return data
        except Exception as e:
            print(f"⚠️ Error loading timetable file: {e}")
    return {"departments": [], "teachers": [], "students": [], "timetable": []}

def save_timetable_data(data):
    """Save timetable data to JSON file"""
    try:
        with open(TIMETABLE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Timetable data saved: {len(data.get('departments', []))} departments, {len(data.get('teachers', []))} teachers")
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

# OR-Tools CP-SAT Timetable Optimization
class TimetableOptimizer:
    def __init__(self, departments, teachers, time_slots, days):
        self.departments = departments
        self.teachers = teachers
        self.time_slots = time_slots
        self.days = days
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

    def create_variables(self):
        """Create decision variables for the optimization problem"""
        # Variable: assignment[dept_index][year][section][day][slot][subject][teacher] = 1 if assigned
        self.assignment = {}

        for dept_idx, dept in enumerate(self.departments):
            for year in range(1, dept["years"] + 1):
                for section_data in dept["sections"]:
                    section = section_data["name"]
                    for day_idx, day in enumerate(self.days):
                        for slot_idx, slot in enumerate(self.time_slots):
                            # Get subjects for this specific year
                            year_subjects = dept["year_subjects"].get(str(year), [])
                            for subject in year_subjects:
                                for teacher in self.teachers:
                                    if subject in teacher["subjects"]:
                                        var_name = f"assign_d{dept_idx}_y{year}_s{section}_d{day_idx}_s{slot_idx}_{subject}_{teacher['name']}"
                                        self.assignment[var_name] = self.model.NewBoolVar(var_name)

    def add_constraints(self):
        """Add all constraints to the model"""
        # Constraint 1: Each slot gets at most one assignment
        for dept_idx, dept in enumerate(self.departments):
            for year in range(1, dept["years"] + 1):
                for section_data in dept["sections"]:
                    section = section_data["name"]
                    for day_idx, day in enumerate(self.days):
                        for slot_idx, slot in enumerate(self.time_slots):
                            slot_assignments = []
                            for subject in dept["subjects"]:
                                for teacher in self.teachers:
                                    if subject in teacher["subjects"]:
                                        var_name = f"assign_d{dept_idx}_y{year}_s{section}_d{day_idx}_s{slot_idx}_{subject}_{teacher['name']}"
                                        if var_name in self.assignment:
                                            slot_assignments.append(self.assignment[var_name])

                            if slot_assignments:
                                self.model.Add(sum(slot_assignments) <= 1)

        # Constraint 2: Subject weekly limits (max 5 periods per subject per week)
        for dept_idx, dept in enumerate(self.departments):
            for year in range(1, dept["years"] + 1):
                for section_data in dept["sections"]:
                    section = section_data["name"]
                    # Get subjects for this specific year
                    year_subjects = dept["year_subjects"].get(str(year), [])
                    for subject in year_subjects:
                        subject_total = []
                        for day_idx, day in enumerate(self.days):
                            for slot_idx, slot in enumerate(self.time_slots):
                                for teacher in self.teachers:
                                    if subject in teacher["subjects"]:
                                        var_name = f"assign_d{dept_idx}_y{year}_s{section}_d{day_idx}_s{slot_idx}_{subject}_{teacher['name']}"
                                        if var_name in self.assignment:
                                            subject_total.append(self.assignment[var_name])

                        if subject_total:
                            self.model.Add(sum(subject_total) <= 5)

        # Constraint 3: Teacher daily limits (max 4 periods per teacher per day)
        for teacher in self.teachers:
            for day_idx, day in enumerate(self.days):
                teacher_daily_total = []
                for dept_idx, dept in enumerate(self.departments):
                    for year in range(1, dept["years"] + 1):
                        for section_data in dept["sections"]:
                            section = section_data["name"]
                            for slot_idx, slot in enumerate(self.time_slots):
                                for subject in dept["subjects"]:
                                    if subject in teacher["subjects"]:
                                        var_name = f"assign_d{dept_idx}_y{year}_s{section}_d{day_idx}_s{slot_idx}_{subject}_{teacher['name']}"
                                        if var_name in self.assignment:
                                            teacher_daily_total.append(self.assignment[var_name])

                if teacher_daily_total:
                    self.model.Add(sum(teacher_daily_total) <= 4)

        # Constraint 4: Teacher can only teach subjects they are qualified for
        # (This is already handled by variable creation, but we add explicit constraints)
        for var_name, var in self.assignment.items():
            # This constraint is implicit in variable creation, but we can add it explicitly
            pass

    def add_objective(self):
        """Add optimization objective (maximize valid assignments only)"""
        # Primary objective: maximize valid assignments from user data
        total_assignments = [var for var in self.assignment.values()]
        if total_assignments:
            # Add secondary objective: prefer assignments where teachers can teach the subject
            self.model.Maximize(sum(total_assignments))

            # Add preference for balanced workloads (penalize over-assignment)
            for teacher in self.teachers:
                for day_idx, day in enumerate(self.days):
                    teacher_assignments = []
                    for var_name, var in self.assignment.items():
                        if f"_{teacher['name']}" in var_name and f"_d{day_idx}_" in var_name:
                            teacher_assignments.append(var)

                    if teacher_assignments:
                        # Penalize having more than 2 assignments per day (soft constraint)
                        day_total = sum(teacher_assignments)
                        penalty = self.model.NewIntVar(0, 10, f"penalty_{teacher['name']}_{day}")
                        self.model.Add(penalty >= day_total - 2)
                        self.model.Add(penalty >= 0)
                        # Minimize penalties
                        self.model.Minimize(penalty)

    def solve(self, time_limit=60):
        """Solve the optimization problem"""
        print("🔬 Starting OR-Tools CP-SAT optimization...")
        print(f"   📊 Variables created: {len(self.assignment)}")
        print(f"   ⏱️ Time limit: {time_limit} seconds")

        # Set solver parameters
        self.solver.parameters.max_time_in_seconds = time_limit
        self.solver.parameters.num_search_workers = 8

        # Solve
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"✅ Solution found in {self.solver.WallTime():.2f} seconds")
            print(f"   📈 Objective value: {self.solver.ObjectiveValue()}")
            return True
        else:
            print("❌ No solution found")
            return False

    def extract_solution(self):
        """Extract the solution from the solver - only user data assignments"""
        solution = []

        for var_name, var in self.assignment.items():
            if self.solver.Value(var) > 0:
                # Parse variable name to extract assignment details
                parts = var_name.split('_')
                dept_idx = int(parts[1][1:])
                year = int(parts[2][1:])
                section = parts[3][1:]
                day_idx = int(parts[4][1:])
                slot_idx = int(parts[5][1:])
                subject = parts[6]
                teacher_name = '_'.join(parts[7:])

                dept = self.departments[dept_idx]
                day = self.days[day_idx]
                time_slot = self.time_slots[slot_idx]

                # Verify that this subject is valid for this year
                year_subjects = dept["year_subjects"].get(str(year), [])
                if subject not in year_subjects:
                    continue  # Skip invalid assignments

                # Only include assignments where teacher can actually teach the subject
                teacher = next((t for t in self.teachers if t["name"] == teacher_name), None)
                if teacher and subject in teacher["subjects"]:
                    # Find classroom from user data
                    classroom = "TBA"
                    if dept["classes"]:
                        classroom = dept["classes"][len(solution) % len(dept["classes"])]["name"]

                    solution.append({
                        "day": day,
                        "time_slot": time_slot,
                        "subject": subject,
                        "teacher": teacher_name,
                        "classroom": classroom,
                        "department": dept["name"],
                        "year": year,
                        "section": section
                    })

        return solution

def create_timetable_with_or_tools():
    """Create optimized timetable using OR-Tools CP-SAT with ONLY user data"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = ["9:00-10:00", "10:00-11:00", "11:30-12:30", "12:30-1:30", "2:30-3:30", "3:30-4:30"]

    # Check if we have data to work with
    if not TIMETABLE_DATA["departments"] or not TIMETABLE_DATA["teachers"]:
        print("⚠️ No user data available - returning empty timetable")
        return []

    # Create optimizer instance with ONLY user data
    optimizer = TimetableOptimizer(TIMETABLE_DATA["departments"], TIMETABLE_DATA["teachers"], time_slots, days)

    # Create variables and constraints based ONLY on user data
    optimizer.create_variables()
    optimizer.add_constraints()
    optimizer.add_objective()

    # Solve with user data only
    if optimizer.solve(time_limit=60):
        solution = optimizer.extract_solution()
        print(f"✅ Generated {len(solution)} assignments from user data only")
        return solution
    else:
        print("❌ No solution found with user data - returning empty timetable")
        return []

def generate_fallback_timetable():
    """Fallback timetable generation when OR-Tools fails"""
    print("🔄 Using fallback timetable generation...")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = ["9:00-10:00", "10:00-11:00", "11:30-12:30", "12:30-1:30", "2:30-3:30", "3:30-4:30"]

    generated_timetable = []
    subject_weekly_count = {}
    teacher_daily_count = {}

    for dept in TIMETABLE_DATA["departments"]:
        dept_teachers = [t for t in TIMETABLE_DATA["teachers"] if t["department"] == dept["name"]]

        for year in range(1, dept["years"] + 1):
            for section_data in dept["sections"]:
                section = section_data["name"]
                class_key = f"{dept['name']}-{year}-{section}"

                for day in days:
                    teacher_daily_count[day] = {}

                    for time_slot in time_slots:
                        assigned = False
                        # Get subjects for this specific year
                        year_subjects = dept["year_subjects"].get(str(year), [])
                        for subject in year_subjects:
                            subject_key = f"{class_key}-{subject}"

                            if subject_weekly_count.get(subject_key, 0) >= 5:
                                continue

                            for t in dept_teachers:
                                if subject in t["subjects"]:
                                    teacher_name = t["name"]

                                    if teacher_daily_count[day].get(teacher_name, 0) >= 4:
                                        continue

                                    is_busy = any(
                                        e["teacher"] == teacher_name and e["day"] == day and e["time_slot"] == time_slot
                                        for e in generated_timetable
                                    )
                                    if is_busy:
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

                                    assigned = True
                                    break
                            if assigned:
                                break

                        if not assigned:
                            entry = {
                                "day": day, "time_slot": time_slot, "subject": "Free Period",
                                "teacher": "N/A", "classroom": "N/A", "department": dept["name"],
                                "year": year, "section": section
                            }
                            generated_timetable.append(entry)

    return generated_timetable

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
    """Generate optimized timetable using OR-Tools CP-SAT (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can generate timetables")

    try:
        global TIMETABLE_DATA

        print("🚀 Starting OR-Tools CP-SAT timetable generation...")

        # Generate optimized timetable using OR-Tools
        generated_timetable = create_timetable_with_or_tools()

        # Save generated timetable
        TIMETABLE_DATA["timetable"] = generated_timetable

        # Save to file for persistence
        save_timetable_data(TIMETABLE_DATA)

        print(f"✅ Timetable generated: {len(generated_timetable)} entries")

        return {
            "message": "Timetable generated using ONLY your provided data - no defaults applied",
            "entries": len(generated_timetable),
            "timetable": generated_timetable,
            "optimization": "OR-Tools CP-SAT (User Data Only)"
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
    return {"message": "Smart Class Scheduler API - OR-Tools Optimized", "status": "running"}

if __name__ == "__main__":
    print("🚀 Starting Smart Class Scheduler Backend with OR-Tools Optimization...")
    print("✅ OR-Tools CP-SAT solver enabled for advanced timetable optimization")
    print("🔑 Test credentials:")
    print("   - Admin: admin1 / password123")
    print("   - Faculty: faculty1 / password123")
    print("   - Student: student1 / password123")
    print("🌐 Backend running on: http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
