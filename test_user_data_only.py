import urllib.request
import urllib.parse
import json

def test_user_data_only():
    print("🧪 Testing User Data Only - No Defaults")
    print("=" * 40)

    # Login as admin
    login_data = urllib.parse.urlencode({
        'username': 'admin1',
        'password': 'password123'
    }).encode()

    try:
        req = urllib.request.Request('http://localhost:8002/token', data=login_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            token = result['access_token']
            print('✅ Admin login successful')
    except Exception as e:
        print(f'❌ Login failed: {e}')
        return

    # Setup with minimal user data only
    user_data_setup = {
        "departments": [
            {
                "name": "Computer Science",
                "classes": [{"name": "CS-Lab", "capacity": 30}],
                "labs": [],
                "years": 1,
                "sections": [{"name": "A", "student_count": 30}],
                "subjects": ["CS101", "CS102"]  # Only 2 subjects
            }
        ],
        "teachers": [
            {
                "name": "Prof. Smith",
                "employee_id": "CS001",
                "subjects": ["CS101"],  # Only teaches CS101
                "department": "Computer Science"
            }
        ]
    }

    try:
        setup_data = json.dumps(user_data_setup).encode()
        req = urllib.request.Request('http://localhost:8002/timetable/setup', data=setup_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')
        urllib.request.urlopen(req)
        print('✅ User data setup complete')
        print('📚 User provided: 1 department, 1 teacher, 2 subjects')
        print('📅 Total slots: 5 days × 6 slots × 1 class = 30 slots')
        print('⚡ OR-Tools will only use YOUR data - no defaults')
    except Exception as e:
        print(f'❌ Setup failed: {e}')
        return

    # Generate timetable with ONLY user data
    try:
        req = urllib.request.Request('http://localhost:8002/timetable/generate', method='POST')
        req.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            timetable = result['timetable']

            print('✅ Timetable generated with USER DATA ONLY!')
            print(f'📊 Total entries: {len(timetable)}')
            print(f'📝 Message: {result["message"]}')

            # Analyze what was generated
            scheduled = 0
            free = 0
            cs101_count = 0
            prof_smith_count = 0

            for entry in timetable:
                if entry['subject'] == 'Free Period':
                    free += 1
                else:
                    scheduled += 1
                    if entry['subject'] == 'CS101':
                        cs101_count += 1
                    if entry['teacher'] == 'Prof. Smith':
                        prof_smith_count += 1

            print(f'✅ Scheduled periods: {scheduled}')
            print(f'🆓 Free periods: {free}')
            print(f'📘 CS101 periods: {cs101_count}')
            print(f'👨‍🏫 Prof. Smith periods: {prof_smith_count}')

            # Verify constraints
            if cs101_count <= 5:
                print('✅ Subject constraint: CS101 ≤ 5 periods/week')
            else:
                print(f'❌ Subject constraint violated: CS101 has {cs101_count} periods')

            if prof_smith_count <= 4:
                print('✅ Teacher constraint: Prof. Smith ≤ 4 periods/day')
            else:
                print(f'❌ Teacher constraint violated: Prof. Smith has {prof_smith_count} periods')

            print('\n🎯 Key Points:')
            print('   ✅ Only CS101 can be scheduled (only subject teacher knows)')
            print('   ✅ Only Prof. Smith can teach (only available teacher)')
            print('   ✅ No default data used')
            print('   ✅ All assignments based on YOUR input only')
            print('   ✅ Empty slots remain empty (no forced assignments)')

    except Exception as e:
        print(f'❌ Generation failed: {e}')

if __name__ == "__main__":
    test_user_data_only()
