import urllib.request
import urllib.parse
import json

# First login to get token
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
    
    # Test password change
    password_data = json.dumps({
        'current_password': 'password123',
        'new_password': 'newpassword123'
    }).encode()
    
    req = urllib.request.Request('http://localhost:8001/users/change-password', data=password_data, method='PUT')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print('✅ Password change successful!')
        print(f'Message: {result["message"]}')
        
except urllib.error.HTTPError as e:
    print(f'❌ Request failed: {e.code}')
    print(f'Error: {e.read().decode()}')
except Exception as e:
    print(f'❌ Error: {e}')
