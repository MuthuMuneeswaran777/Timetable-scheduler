import urllib.request
import urllib.parse
import json
import time

print('Testing system after start_clean.bat...')
print('=' * 40)

# Wait for servers to start
time.sleep(3)

try:
    # Test backend
    with urllib.request.urlopen('http://localhost:8001/') as response:
        result = json.loads(response.read().decode())
        print('✅ Backend running on port 8001')

    # Test login
    login_data = urllib.parse.urlencode({
        'username': 'admin1',
        'password': 'password123'
    }).encode()

    req = urllib.request.Request('http://localhost:8001/token',
                               data=login_data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        token = result['access_token']
        print('✅ Login successful')

    # Test data
    req = urllib.request.Request('http://localhost:8001/timetable/data', method='GET')
    req.add_header('Authorization', f'Bearer {token}')

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        depts = len(data.get('departments', []))
        teachers = len(data.get('teachers', []))
        students = len(data.get('students', []))

        print('✅ Dashboard data loaded')
        print(f'   Departments: {depts}')
        print(f'   Teachers: {teachers}')
        print(f'   Students: {students}')

except Exception as e:
    print('❌ Error:', e)

print()
print('🎉 System Status:')
print('   Frontend: http://localhost:3000')
print('   Backend: http://localhost:8001')
print('   Login: admin1 / password123')
