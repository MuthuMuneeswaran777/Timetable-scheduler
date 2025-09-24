@echo off
echo Smart Class Scheduler - Frontend Startup
echo ========================================
echo.

echo Checking for processes on port 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo Killing existing process %%a on port 3000
    taskkill /PID %%a /F >nul 2>&1
)

echo Checking for processes on port 3001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
    echo Killing existing process %%a on port 3001
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Starting React frontend...
echo ✅ Port 3000 is now available
echo 🔗 Frontend will be available at: http://localhost:3000
echo.

npm start
