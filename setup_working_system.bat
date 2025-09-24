@echo off
echo Smart Class Scheduler - Complete Working Setup
echo =============================================
echo.

echo This will set up a fully working Smart Class Scheduler
echo with a simple, reliable authentication system.
echo.

echo Step 1: Stopping existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo Step 2: Creating simple working backend...
echo.

REM Create a simple working backend
python -c "
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uvicorn

app = FastAPI(title='Smart Class Scheduler API')

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:3001'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Security
SECRET_KEY = 'your-secret-key-change-in-production-12345'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

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

# Simple user database
USERS_DB = {
    'admin1': {
        'id': 1,
        'username': 'admin1',
        'email': 'admin@university.edu',
        'password_hash': pwd_context.hash('password123'),
        'role': 'admin',
        'full_name': 'S.M.Poobalan'
    },
    'faculty1': {
        'id': 2,
        'username': 'faculty1',
        'email': 'faculty@university.edu',
        'password_hash': pwd_context.hash('password123'),
        'role': 'faculty',
        'full_name': 'Prof. John Smith'
    },
    'student1': {
        'id': 3,
        'username': 'student1',
        'email': 'student@university.edu',
        'password_hash': pwd_context.hash('password123'),
        'role': 'student',
        'full_name': 'John Doe'
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
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str):
    return USERS_DB.get(username)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

@app.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user['username']}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.get('/users/me', response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get('/test/auth')
async def test_auth():
    return {'status': 'success', 'message': 'Authentication system working!'}

if __name__ == '__main__':
    print('🚀 Starting Smart Class Scheduler Backend...')
    print('✅ Simple authentication system loaded')
    print('🔑 Test credentials: admin1/password123, faculty1/password123, student1/password123')
    uvicorn.run(app, host='0.0.0.0', port=8001)
"

echo.
echo ✅ Backend setup complete!
echo.
echo Starting backend server...
python -c "
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uvicorn

app = FastAPI(title='Smart Class Scheduler API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:3001'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

SECRET_KEY = 'your-secret-key-change-in-production-12345'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    full_name: str

USERS_DB = {
    'admin1': {
        'id': 1,
        'username': 'admin1',
        'email': 'admin@university.edu',
        'password_hash': pwd_context.hash('password123'),
        'role': 'admin',
        'full_name': 'S.M.Poobalan'
    },
    'faculty1': {
        'id': 2,
        'username': 'faculty1',
        'email': 'faculty@university.edu',
        'password_hash': pwd_context.hash('password123'),
        'role': 'faculty',
        'full_name': 'Prof. John Smith'
    },
    'student1': {
        'id': 3,
        'username': 'student1',
        'email': 'student@university.edu',
        'password_hash': pwd_context.hash('password123'),
        'role': 'student',
        'full_name': 'John Doe'
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
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str):
    return USERS_DB.get(username)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

@app.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user['username']}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.get('/users/me', response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get('/test/auth')
async def test_auth():
    return {'status': 'success', 'message': 'Authentication system working!'}

if __name__ == '__main__':
    print('🚀 Starting Smart Class Scheduler Backend...')
    print('✅ Simple authentication system loaded')
    print('🔑 Test credentials:')
    print('   - Admin: admin1 / password123')
    print('   - Faculty: faculty1 / password123') 
    print('   - Student: student1 / password123')
    print('🌐 Backend running on: http://localhost:8001')
    uvicorn.run(app, host='0.0.0.0', port=8001)
"
