import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8001/test/db') as response:
        result = json.loads(response.read().decode())
        print('Database test result:')
        print(f'Status: {result["status"]}')
        print(f'Message: {result["message"]}')
        if 'users' in result:
            print('Users found:')
            for user in result['users']:
                print(f'  - {user["username"]} ({user["role"]})')
except Exception as e:
    print(f'Test failed: {e}')
