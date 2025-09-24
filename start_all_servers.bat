@echo off
echo Smart Class Scheduler - Complete Startup Script
echo ===============================================
echo.

echo Step 1: Cleaning up existing processes...
echo.

REM Kill existing Python processes (backend)
echo Stopping backend processes...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Backend processes stopped
) else (
    echo ℹ️  No backend processes to stop
)

REM Kill processes on port 8000 (backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing process %%a on port 8000
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill processes on port 3000 (frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo Killing process %%a on port 3000
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill processes on port 3001 (frontend alternative)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
    echo Killing process %%a on port 3001
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Step 2: Starting Backend Server...
echo.

REM Activate virtual environment and start backend
call .venv\Scripts\activate.bat
echo ✅ Virtual environment activated

echo Starting FastAPI backend on port 8000...
start "Smart Class Scheduler - Backend" cmd /k "python backend.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 3: Starting Frontend Server...
echo.

echo Starting React frontend...
start "Smart Class Scheduler - Frontend" cmd /k "npm start"

echo.
echo ✅ Startup Complete!
echo.
echo Services:
echo 🔗 Backend API: http://localhost:8000
echo 🔗 API Docs: http://localhost:8000/docs
echo 🔗 Frontend: http://localhost:3000 (or 3001 if 3000 is busy)
echo.
echo Login Credentials:
echo 👤 Admin: admin1 / password123
echo 👤 Faculty: faculty1 / password123
echo 👤 Student: student1 / password123
echo.
echo Both servers are starting in separate windows.
echo Close this window when both servers are running.
echo.
pause
