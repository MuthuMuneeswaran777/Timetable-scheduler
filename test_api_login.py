import urllib.request
import urllib.parse
import json

# Test login API
data = urllib.parse.urlencode({
    'username': 'admin1',
    'password': 'password123'
}).encode()

try:
    req = urllib.request.Request('http://localhost:8001/token', data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print('✅ API Login successful!')
        print(f'Token type: {result["token_type"]}')
        print(f'Token length: {len(result["access_token"])} characters')
        
except urllib.error.HTTPError as e:
    print(f'❌ API Login failed: {e.code}')
    print(f'Error: {e.read().decode()}')
except Exception as e:
    print(f'❌ Connection error: {e}')
