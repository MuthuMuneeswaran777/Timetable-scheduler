import urllib.request
import urllib.parse
import json

def test_debug_setup():
    print("🧪 Debug Setup Test")
    print("=" * 20)

    # Login as admin
    login_data = urllib.parse.urlencode({
        'username': 'admin1',
        'password': 'password123'
    }).encode()

    try:
        req = urllib.request.Request('http://localhost:8003/token', data=login_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            token = result['access_token']
            print('✅ Admin login successful')
    except Exception as e:
        print(f'❌ Login failed: {e}')
        return

    # Minimal setup
    minimal_setup = {
        "departments": [
            {
                "name": "Test Dept",
                "classes": [{"name": "Room1", "capacity": 30}],
                "labs": [],
                "years": 1,
                "sections": [{"name": "A", "student_count": 10}],
                "year_subjects": {
                    "1": ["SUB101", "SUB102"]
                }
            }
        ],
        "teachers": [
            {
                "name": "Test Teacher",
                "employee_id": "T001",
                "subjects": ["SUB101"],
                "department": "Test Dept"
            }
        ]
    }

    print("📊 Sending data:")
    print(json.dumps(minimal_setup, indent=2))

    try:
        setup_data = json.dumps(minimal_setup).encode()
        req = urllib.request.Request('http://localhost:8003/timetable/setup', data=setup_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')

        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        print('✅ Setup successful!')
        print(f"📝 Response: {result}")

    except Exception as e:
        print(f'❌ Setup failed: {e}')

if __name__ == "__main__":
    test_debug_setup()
