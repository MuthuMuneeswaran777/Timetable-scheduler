from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import os

from backend.database import get_db
from backend.models import Admin

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours


class AdminSignup(BaseModel):
    email: EmailStr
    password: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    admin_email: str


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated admin"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin = db.scalars(select(Admin).where(Admin.email == email)).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin


@router.post("/signup", response_model=TokenResponse)
def signup(admin_data: AdminSignup, db: Session = Depends(get_db)):
    """Admin signup - only allowed if no admin exists"""
    # Check if any admin already exists
    existing_admin = db.scalars(select(Admin)).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin already exists. Only one admin is allowed."
        )
    
    # Create new admin
    hashed_password = hash_password(admin_data.password)
    admin = Admin(
        email=admin_data.email,
        password_hash=hashed_password,
        created_at=datetime.utcnow()
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # Create access token
    access_token = create_access_token(data={"sub": admin.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        admin_email=admin.email
    )


@router.post("/login", response_model=TokenResponse)
def login(admin_data: AdminLogin, db: Session = Depends(get_db)):
    """Admin login"""
    admin = db.scalars(select(Admin).where(Admin.email == admin_data.email)).first()
    
    if not admin or not verify_password(admin_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": admin.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        admin_email=admin.email
    )


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Change admin password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_admin.password_hash = hash_password(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/me")
def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    """Get current admin information"""
    return {
        "admin_id": current_admin.admin_id,
        "email": current_admin.email,
        "created_at": current_admin.created_at,
        "last_login": current_admin.last_login
    }


@router.get("/check-admin-exists")
def check_admin_exists(db: Session = Depends(get_db)):
    """Check if admin already exists"""
    admin_exists = db.scalars(select(Admin)).first() is not None
    return {"admin_exists": admin_exists}
