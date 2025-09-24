import urllib.request
import json

print('Testing backend connectivity...')
try:
    with urllib.request.urlopen('http://localhost:8001/') as response:
        result = json.loads(response.read().decode())
        print('✅ Backend running on port 8001')

    import urllib.parse
    login_data = urllib.parse.urlencode({
        'username': 'admin1',
        'password': 'password123'
    }).encode()

    req = urllib.request.Request('http://localhost:8001/token',
                               data=login_data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print('✅ Login system working')

    req = urllib.request.Request('http://localhost:8001/timetable/data', method='GET')
    req.add_header('Authorization', f'Bearer {result["access_token"]}')

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print('✅ Timetable data endpoint working')
        print(f'   Departments: {len(data.get("departments", []))}')
        print(f'   Teachers: {len(data.get("teachers", []))}')
        print(f'   Students: {len(data.get("students", []))}')

    print('🎉 Backend is ready!')

except Exception as e:
    print('❌ Backend error:', e)
