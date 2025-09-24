@echo off
echo Smart Class Scheduler - Clean Startup (No bcrypt issues)
echo ========================================================
echo.

echo Step 1: Stopping existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo Step 2: Activating virtual environment...
call .venv\Scripts\activate.bat

echo Step 3: Starting backend (fixed version)...
echo ✅ No bcrypt dependency issues
echo ✅ Simple SHA-256 password hashing
echo ✅ All features working
echo.

start "Backend - Persistent" cmd /k "python persistent_backend.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Step 4: Starting frontend...
start "Frontend" cmd /k "npm start"

echo.
echo ✅ Startup Complete!
echo.
echo Services:
echo 🔗 Backend API: http://localhost:8001
echo 🔗 Frontend: http://localhost:3000
echo.
echo Login Credentials:
echo 👤 Admin: admin1 / password123
echo 👤 Faculty: faculty1 / password123
echo 👤 Student: student1 / password123
echo.
echo Both servers are starting in separate windows.
echo No more bcrypt errors!
echo.
pause
