@echo off
echo Smart Class Scheduler - MySQL Password Configuration
echo ====================================================
echo.
echo ✅ MySQL Server is running on your system (port 3306)
echo ❌ But we need the correct root password
echo.
echo OPTION A: Find Your MySQL Password
echo ==================================
echo.
echo If you installed MySQL yourself:
echo 1. Check if you remember the root password you set during installation
echo 2. Try common passwords: (empty), root, password, admin, 123456
echo.
echo If you have XAMPP installed:
echo 1. Open XAMPP Control Panel
echo 2. Click "Admin" next to MySQL (opens phpMyAdmin)
echo 3. If it opens without asking for password, then password is empty
echo.
echo If you have MySQL Workbench:
echo 1. Open MySQL Workbench
echo 2. Try to connect to localhost with root user
echo 3. Use the password that works
echo.
echo OPTION B: Reset MySQL Root Password
echo ===================================
echo.
echo Method 1 - Using MySQL Command Line:
echo 1. Open Command Prompt as Administrator
echo 2. Navigate to MySQL bin directory (usually C:\Program Files\MySQL\MySQL Server 8.0\bin)
echo 3. Run: mysql -u root -p
echo 4. Enter your password when prompted
echo.
echo Method 2 - Reset Password (Advanced):
echo 1. Stop MySQL service: net stop mysql80
echo 2. Start MySQL in safe mode: mysqld --skip-grant-tables
echo 3. Connect: mysql -u root
echo 4. Reset: ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword';
echo 5. Restart MySQL service: net start mysql80
echo.
echo OPTION C: Use Different MySQL Setup
echo ===================================
echo.
echo Install XAMPP (Easier):
echo 1. Download from: https://www.apachefriends.org/
echo 2. Install XAMPP
echo 3. Start MySQL from XAMPP Control Panel
echo 4. Default password is usually empty
echo.
echo.
echo MANUAL PASSWORD TEST:
echo ====================
echo.
set /p mysql_password="Enter your MySQL root password (or press Enter for empty): "

echo.
echo Testing connection with provided password...
python -c "
import mysql.connector
try:
    conn = mysql.connector.connect(host='localhost', user='root', password='%mysql_password%')
    print('✅ Connection successful!')
    
    # Create database
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS smart_class_scheduler')
    cursor.execute('USE smart_class_scheduler')
    print('✅ Database created/selected')
    
    # Test if tables exist
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    if tables:
        print('✅ Tables found:', len(tables))
    else:
        print('⚠️  No tables found - need to run schema')
    
    conn.close()
    
    # Update .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    content = content.replace('DB_PASSWORD=', 'DB_PASSWORD=%mysql_password%')
    
    with open('.env', 'w') as f:
        f.write(content)
    
    print('✅ Updated .env file with password')
    
except Exception as e:
    print('❌ Connection failed:', str(e))
    print('Please check your password and try again')
"

if %errorlevel%==0 (
    echo.
    echo ✅ MySQL setup successful!
    echo Now running the database schema...
    echo.
    
    REM Run database schema
    python -c "
import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', password='%mysql_password%', database='smart_class_scheduler')
cursor = conn.cursor()

# Read and execute schema
with open('database_schema.sql', 'r') as f:
    schema = f.read()

# Split by semicolon and execute each statement
statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
for stmt in statements:
    if stmt and not stmt.startswith('--'):
        try:
            cursor.execute(stmt)
        except Exception as e:
            if 'already exists' not in str(e).lower():
                print('Warning:', e)

conn.commit()
print('✅ Database schema created')

# Read and execute sample data
with open('sample_data.sql', 'r') as f:
    data = f.read()

statements = [stmt.strip() for stmt in data.split(';') if stmt.strip()]
for stmt in statements:
    if stmt and not stmt.startswith('--'):
        try:
            cursor.execute(stmt)
        except Exception as e:
            if 'duplicate entry' not in str(e).lower():
                print('Warning:', e)

conn.commit()
print('✅ Sample data inserted')
conn.close()
"
    
    echo.
    echo ✅ Database setup complete!
    echo Starting backend server...
    python backend.py
) else (
    echo.
    echo ❌ Setup failed. Please check your MySQL password.
    echo.
    echo Helpful commands:
    echo - Check MySQL service: sc query mysql80
    echo - Open MySQL Workbench to test connection
    echo - Or install XAMPP for easier setup
)

pause
