import urllib.request
import urllib.parse
import json

def test_simple_year_wise():
    print("🧪 Testing Simple Year-Wise Setup")
    print("=" * 30)

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

    # Very simple setup
    simple_setup = {
        "departments": [
            {
                "name": "Computer Science",
                "classes": [{"name": "CS-Lab", "capacity": 30}],
                "labs": [],
                "years": 2,
                "sections": [{"name": "A", "student_count": 30}],
                "year_subjects": {
                    "1": ["CS101", "CS102"],
                    "2": ["CS201", "CS202"]
                }
            }
        ],
        "teachers": [
            {
                "name": "Prof. Smith",
                "employee_id": "CS001",
                "subjects": ["CS101", "CS102", "CS201"],
                "department": "Computer Science"
            }
        ]
    }

    try:
        setup_data = json.dumps(simple_setup).encode()
        req = urllib.request.Request('http://localhost:8002/timetable/setup', data=setup_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')
        urllib.request.urlopen(req)
        print('✅ Simple setup complete')
    except Exception as e:
        print(f'❌ Setup failed: {e}')
        return

    # Generate timetable
    try:
        req = urllib.request.Request('http://localhost:8002/timetable/generate', method='POST')
        req.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            timetable = result['timetable']

            print('✅ Simple year-wise timetable generated!')
            print(f'📊 Total entries: {len(timetable)}')

            # Check for year-wise subjects
            year1_subjects = set()
            year2_subjects = set()

            for entry in timetable:
                if entry['subject'] == 'Free Period':
                    continue
                if entry['year'] == 1:
                    year1_subjects.add(entry['subject'])
                elif entry['year'] == 2:
                    year2_subjects.add(entry['subject'])

            print(f'📖 Year 1 subjects: {sorted(year1_subjects)}')
            print(f'📖 Year 2 subjects: {sorted(year2_subjects)}')

            if year1_subjects == {'CS101', 'CS102'} and year2_subjects == {'CS201', 'CS202'}:
                print('✅ Perfect! Year-wise subjects working correctly!')
            else:
                print('⚠️ Some subjects mixed between years')

    except Exception as e:
        print(f'❌ Generation failed: {e}')

if __name__ == "__main__":
    test_simple_year_wise()
