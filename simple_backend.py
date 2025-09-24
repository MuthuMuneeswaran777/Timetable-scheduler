from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uvicorn

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# Simple user database - this works without MySQL
USERS_DB = {
    "admin1": {
        "id": 1,
        "username": "admin1",
        "email": "admin@university.edu",
        "password_hash": pwd_context.hash("password123"),
        "role": "admin",
        "full_name": "S.M.Poobalan"
    },
    "faculty1": {
        "id": 2,
        "username": "faculty1",
        "email": "faculty@university.edu",
        "password_hash": pwd_context.hash("password123"),
        "role": "faculty",
        "full_name": "Prof. John Smith"
    },
    "student1": {
        "id": 3,
        "username": "student1",
        "email": "student@university.edu",
        "password_hash": pwd_context.hash("password123"),
        "role": "student",
        "full_name": "John Doe"
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

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

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str

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
        new_password_hash = pwd_context.hash(request.new_password)
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
    
    # Generate new user ID
    new_id = max([user["id"] for user in USERS_DB.values()]) + 1
    
    # Create new user
    USERS_DB[request.username] = {
        "id": new_id,
        "username": request.username,
        "email": request.email,
        "password_hash": pwd_context.hash(request.password),
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

@app.get("/test/auth")
async def test_auth():
    return {"status": "success", "message": "Authentication system working!"}

@app.get("/")
async def root():
    return {"message": "Smart Class Scheduler API", "status": "running"}

if __name__ == "__main__":
    print("🚀 Starting Smart Class Scheduler Backend...")
    print("✅ Simple authentication system loaded")
    print("🔑 Test credentials:")
    print("   - Admin: admin1 / password123")
    print("   - Faculty: faculty1 / password123") 
    print("   - Student: student1 / password123")
    print("🌐 Backend running on: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
