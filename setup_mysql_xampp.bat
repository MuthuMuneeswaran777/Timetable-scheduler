@echo off
echo Smart Class Scheduler - MySQL Setup with XAMPP
echo ===============================================
echo.
echo Step 1: Download XAMPP
echo ---------------------
echo 1. Open your web browser
echo 2. Go to: https://www.apachefriends.org/download.html
echo 3. Download XAMPP for Windows (latest version)
echo 4. Run the installer as Administrator
echo.
echo Step 2: Install XAMPP
echo --------------------
echo 1. Choose installation directory (default: C:\xampp)
echo 2. Select components: Apache, MySQL, PHP, phpMyAdmin
echo 3. Complete the installation
echo.
echo Step 3: Start MySQL Service
echo ---------------------------
echo 1. Open XAMPP Control Panel (as Administrator)
echo 2. Click "Start" next to MySQL
echo 3. MySQL should show "Running" status
echo.
echo Step 4: Create Database
echo ----------------------
echo 1. Click "Admin" button next to MySQL (opens phpMyAdmin)
echo 2. Click "SQL" tab in phpMyAdmin
echo 3. Copy contents of database_schema.sql and paste, click "Go"
echo 4. Copy contents of sample_data.sql and paste, click "Go"
echo.
echo Step 5: Update Configuration
echo ----------------------------
echo 1. Open .env file in your project
echo 2. Change DB_PASSWORD to empty: DB_PASSWORD=
echo 3. Save the file
echo.
echo Step 6: Restart Backend
echo ----------------------
echo 1. Stop current backend (Ctrl+C)
echo 2. Run: python backend.py
echo 3. Should show: "Database connection pool created successfully"
echo.
echo Press any key when you've completed the installation...
pause
echo.
echo Opening XAMPP download page...
start https://www.apachefriends.org/download.html
echo.
echo After installation, run this script again to continue setup.
pause
