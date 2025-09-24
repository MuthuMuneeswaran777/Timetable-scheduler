@echo off
echo Smart Class Scheduler - MySQL Setup Guide
echo ==========================================
echo.
echo To fix the database connection error, you have 3 options:
echo.
echo OPTION 1: Set MySQL Password (Recommended)
echo ------------------------------------------
echo 1. Open MySQL Command Line Client or MySQL Workbench
echo 2. Connect to MySQL as root
echo 3. Run: ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_password';
echo 4. Update the .env file with your password
echo.
echo OPTION 2: Allow Empty Password (Less Secure)
echo ---------------------------------------------
echo 1. Open MySQL Command Line Client or MySQL Workbench
echo 2. Connect to MySQL as root
echo 3. Run: ALTER USER 'root'@'localhost' IDENTIFIED BY '';
echo 4. Keep .env file DB_PASSWORD empty
echo.
echo OPTION 3: Use Demo Mode (Current Setup)
echo ---------------------------------------
echo The application will run with mock data without database connection.
echo All features work but data is not persistent.
echo.
echo Current .env configuration:
echo DB_HOST=localhost
echo DB_USER=root
echo DB_PASSWORD=your_mysql_password  ^<-- Update this with your MySQL password
echo DB_NAME=smart_class_scheduler
echo.
echo After updating .env file, restart the backend server.
echo.
pause
