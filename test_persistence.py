import urllib.request
import urllib.parse
import json

# First login as admin
login_data = urllib.parse.urlencode({
    'username': 'admin1',
    'password': 'password123'
}).encode()

try:
    # Login
    req = urllib.request.Request('http://localhost:8001/token', data=login_data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        token = result['access_token']
        print('✅ Login successful, got token')
    
    # Create a new user
    user_data = json.dumps({
        'username': 'testuser1',
        'email': 'test@university.edu',
        'password': 'testpass123',
        'full_name': 'Test User',
        'role': 'student'
    }).encode()
    
    req = urllib.request.Request('http://localhost:8001/users/', data=user_data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print('✅ User created successfully!')
        print(f'New user: {result["username"]} ({result["role"]})')
        
    # List all users to verify
    req = urllib.request.Request('http://localhost:8001/users/', method='GET')
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as response:
        users = json.loads(response.read().decode())
        print(f'📋 Total users now: {len(users)}')
        for user in users:
            print(f'   👤 {user["username"]} ({user["role"]})')
        
except urllib.error.HTTPError as e:
    print(f'❌ Request failed: {e.code}')
    print(f'Error: {e.read().decode()}')
except Exception as e:
    print(f'❌ Error: {e}')
