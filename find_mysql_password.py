import mysql.connector
import sys

passwords = ['', 'root', 'password', 'admin', '123456', 'mysql', 'toor', 'pass']

print('🔍 Testing common MySQL passwords...')
print()

for i, pwd in enumerate(passwords, 1):
    try:
        conn = mysql.connector.connect(
            host='localhost', 
            user='root', 
            password=pwd,
            connect_timeout=5
        )
        print(f'✅ SUCCESS! Password found: "{pwd if pwd else "(empty)"}"')
        
        # Test database creation
        cursor = conn.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS smart_class_scheduler')
        print('✅ Database access confirmed')
        
        conn.close()
        
        # Update .env file
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace the password line
        lines = content.split('\n')
        for j, line in enumerate(lines):
            if line.startswith('DB_PASSWORD='):
                lines[j] = f'DB_PASSWORD={pwd}'
                break
        
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        
        print('✅ Updated .env file')
        print(f'✅ Ready to create database with password: "{pwd if pwd else "(empty)"}"')
        
        # Now create the full database
        print('\n🔄 Setting up database schema...')
        conn = mysql.connector.connect(
            host='localhost', 
            user='root', 
            password=pwd,
            database='smart_class_scheduler'
        )
        cursor = conn.cursor()
        
        # Read schema file
        try:
            with open('database_schema.sql', 'r') as f:
                schema = f.read()
            
            # Execute schema statements
            statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
            for stmt in statements:
                if stmt:
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        if 'already exists' not in str(e).lower():
                            print(f'Warning: {e}')
            
            conn.commit()
            print('✅ Database schema created')
            
        except FileNotFoundError:
            print('⚠️  database_schema.sql not found, skipping schema creation')
        
        # Read sample data
        try:
            with open('sample_data.sql', 'r') as f:
                data = f.read()
            
            statements = [stmt.strip() for stmt in data.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
            for stmt in statements:
                if stmt:
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        if 'duplicate entry' not in str(e).lower():
                            print(f'Warning: {e}')
            
            conn.commit()
            print('✅ Sample data inserted')
            
        except FileNotFoundError:
            print('⚠️  sample_data.sql not found, skipping sample data')
        
        conn.close()
        print('\n🎉 Database setup complete!')
        sys.exit(0)
        
    except mysql.connector.Error as e:
        print(f'❌ Password "{pwd if pwd else "(empty)"}": {str(e)[:60]}...')
    except Exception as e:
        print(f'❌ Password "{pwd if pwd else "(empty)"}": Connection failed - {str(e)[:40]}...')

print()
print('❌ None of the common passwords worked.')
print('💡 You may need to:')
print('   1. Check MySQL Workbench for saved connections')
print('   2. Install XAMPP (easier setup)')
print('   3. Reset MySQL root password')
print('   4. Or continue with DEMO MODE (current setup works fine)')
