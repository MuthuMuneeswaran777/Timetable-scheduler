@echo off
echo Smart Class Scheduler - Database Setup Verification
echo ===================================================
echo.
echo Testing MySQL connection...
echo.

REM Check if XAMPP MySQL is running
netstat -ano | findstr :3306 >nul
if %errorlevel%==0 (
    echo ✅ MySQL service is running on port 3306
) else (
    echo ❌ MySQL service is not running
    echo Please start MySQL in XAMPP Control Panel
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Testing database connection...
python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password=''); print('✅ Database connection successful!'); conn.close()" 2>nul
if %errorlevel%==0 (
    echo ✅ Database connection test passed
) else (
    echo ❌ Database connection failed
    echo Please check XAMPP MySQL service
    pause
    exit /b 1
)

echo.
echo Creating database and tables...
python -c "
import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', password='')
cursor = conn.cursor()
cursor.execute('CREATE DATABASE IF NOT EXISTS smart_class_scheduler')
cursor.execute('USE smart_class_scheduler')
print('✅ Database created successfully')
conn.close()
"

echo.
echo Database setup complete! Starting backend...
python backend.py

pause
