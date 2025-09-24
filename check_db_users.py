import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root', 
    password='Avm@23281501',
    database='smart_class_scheduler'
)
cursor = conn.cursor(dictionary=True)

print('📋 Users in database:')
cursor.execute('SELECT username, role FROM Users')
users = cursor.fetchall()

for user in users:
    print(f'   👤 {user["username"]} ({user["role"]})')

print()
print('🔍 Testing query for admin1:')
cursor.execute('SELECT username, role FROM Users WHERE username = %s', ('admin1',))
result = cursor.fetchone()
if result:
    print(f'   ✅ Found: {result["username"]}')
else:
    print('   ❌ Not found!')

conn.close()
