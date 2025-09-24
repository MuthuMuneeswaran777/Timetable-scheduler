import mysql.connector
from passlib.context import CryptContext

# Test database connection and user data
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root', 
        password='Avm@23281501',
        database='smart_class_scheduler'
    )
    cursor = conn.cursor(dictionary=True)
    
    # Check if users exist
    cursor.execute('SELECT username, password_hash, role FROM Users')
    users = cursor.fetchall()
    
    print('📋 Users in database:')
    for user in users:
        print(f'   👤 {user["username"]} ({user["role"]})')
    
    # Test password verification
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    test_password = 'password123'
    
    print()
    print('🔐 Testing password verification:')
    for user in users:
        is_valid = pwd_context.verify(test_password, user['password_hash'])
        status = '✅' if is_valid else '❌'
        print(f'   {status} {user["username"]}: {is_valid}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Database error: {e}')
    print('🔄 Will use mock data instead')
