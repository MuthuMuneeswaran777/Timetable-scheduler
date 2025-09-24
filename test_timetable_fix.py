import urllib.request
import urllib.parse
import json

# Test the timetable creation with the fix
def test_timetable_creation():
    print("🧪 Testing Timetable Creation Fix")
    print("=" * 40)
    
    # Login as admin
    login_data = urllib.parse.urlencode({
        'username': 'admin1',
        'password': 'password123'
    }).encode()

    try:
        req = urllib.request.Request('http://localhost:8001/token', data=login_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            token = result['access_token']
            print('✅ Admin login successful')
    except Exception as e:
        print(f'❌ Login failed: {e}')
        return

    # Simple timetable setup
    timetable_setup = {
        "departments": [
            {
                "name": "Computer Science",
                "classes": [
                    {"name": "CS-101", "capacity": 60}
                ],
                "labs": [
                    {"name": "CS-Lab-1", "capacity": 30}
                ],
                "years": 4,
                "sections": [
                    {"name": "A", "student_count": 30}
                ],
                "subjects": [
                    "Programming",
                    "Data Structures"
                ]
            }
        ],
        "teachers": [
            {
                "name": "Dr. John Smith",
                "employee_id": "CS001",
                "subjects": ["Programming", "Data Structures"],
                "department": "Computer Science"
            }
        ]
    }

    try:
        setup_data = json.dumps(timetable_setup).encode()
        req = urllib.request.Request('http://localhost:8001/timetable/setup', data=setup_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print('✅ Timetable setup completed successfully!')
            print(f"📊 Summary:")
            print(f"   📚 Departments: {result['summary']['departments']}")
            print(f"   👨‍🏫 Teachers: {result['summary']['teachers']}")
            print(f"   👨‍🎓 Students: {result['summary']['students']}")
            print(f"   🔑 Accounts Created: {result['summary']['accounts_created']}")
            
            # Test login with created accounts
            print("\n🧪 Testing Auto-Created Accounts:")
            
            # Test faculty login
            faculty_login = urllib.parse.urlencode({
                'username': 'CS001',
                'password': 'CS001'
            }).encode()
            
            req = urllib.request.Request('http://localhost:8001/token', data=faculty_login, method='POST')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print('✅ Faculty login successful: CS001')
            
            # Test student login
            student_login = urllib.parse.urlencode({
                'username': 'COM1A001',
                'password': 'COM1A001'
            }).encode()
            
            req = urllib.request.Request('http://localhost:8001/token', data=student_login, method='POST')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print('✅ Student login successful: COM1A001')
            
            print("\n🎉 All tests passed! The fix is working correctly.")
            
    except urllib.error.HTTPError as e:
        print(f'❌ Setup failed: {e.code}')
        print(f'Error: {e.read().decode()}')
    except Exception as e:
        print(f'❌ Setup error: {e}')

if __name__ == "__main__":
    test_timetable_creation()
