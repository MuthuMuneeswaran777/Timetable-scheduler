@echo off
echo Smart Class Scheduler - Auto Server Restart
echo ===========================================
echo.

echo Checking for processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing process %%a on port 8000
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting backend server...
echo ✅ Database connection: MySQL with real data
echo ✅ Backend URL: http://localhost:8000
echo ✅ Frontend URL: http://localhost:3001
echo.
echo Login credentials:
echo - Admin: admin1 / password123
echo - Faculty: faculty1 / password123
echo - Student: student1 / password123
echo.

python backend.py
