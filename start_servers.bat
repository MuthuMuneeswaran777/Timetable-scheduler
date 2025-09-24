@echo off
echo Smart Class Scheduler - Server Startup
echo =======================================
echo.

echo Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing existing process %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Starting Backend Server (FastAPI)...
start "Backend Server" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python backend.py"

echo.
echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo Backend Status:
echo - FastAPI Server: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo - Database: Demo Mode (Mock Data)
echo.

echo Frontend is running on: http://localhost:3001
echo.
echo Ready to use! Login credentials:
echo - Admin: admin1 / password123
echo - Faculty: faculty1 / password123  
echo - Student: student1 / password123
echo.
pause
