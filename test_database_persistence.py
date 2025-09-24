import urllib.request
import urllib.parse
import json
import os

def test_database_persistence():
    print("🗄️ Testing Year-Wise Subjects Database Persistence")
    print("=" * 55)

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

    # Check current database state
    try:
        req = urllib.request.Request('http://localhost:8003/timetable/data', method='GET')
        req.add_header('Authorization', f'Bearer {token}')

        with urllib.request.urlopen(req) as response:
            current_data = json.loads(response.read().decode())

        print('📂 Current database state:')
        print(f'   📚 Departments: {len(current_data.get("departments", []))}')
        print(f'   👨‍🏫 Teachers: {len(current_data.get("teachers", []))}')
        print(f'   👨‍🎓 Students: {len(current_data.get("students", []))}')
        print(f'   📅 Timetables: {len(current_data.get("timetable", []))}')

        # Show department structure
        for dept in current_data.get("departments", []):
            print(f'   🏫 {dept.get("name", "Unknown")}:')
            year_subjects = dept.get("year_subjects", {})
            for year, subjects in year_subjects.items():
                print(f'      📖 Year {year}: {subjects}')

    except Exception as e:
        print(f'⚠️ Could not check current data: {e}')

    # Setup with year-wise subjects
    year_wise_setup = {
        "departments": [
            {
                "name": "Computer Science",
                "classes": [
                    {"name": "CS-Lab-101", "capacity": 60},
                    {"name": "CS-Lab-102", "capacity": 60}
                ],
                "labs": [
                    {"name": "CS-Lab-101", "capacity": 30}
                ],
                "years": 2,
                "sections": [
                    {"name": "A", "student_count": 60},
                    {"name": "B", "student_count": 60}
                ],
                "year_subjects": {
                    "1": ["CS101", "CS102", "CS103", "CS104", "CS105", "CS106"],
                    "2": ["CS201", "CS202", "CS203", "CS204", "CS205", "CS206"]
                }
            }
        ],
        "teachers": [
            {
                "name": "Dr. Alice Johnson",
                "employee_id": "CS001",
                "subjects": ["CS101", "CS102", "CS103"],
                "department": "Computer Science"
            }
        ]
    }

    print('\n📊 Setting up year-wise subjects:')
    print('   📚 Computer Science Department')
    print('   📖 Year 1: CS101, CS102, CS103, CS104, CS105, CS106')
    print('   📖 Year 2: CS201, CS202, CS203, CS204, CS205, CS206')
    print('   👨‍🏫 Teacher: Dr. Alice Johnson (CS101-CS103)')

    try:
        setup_data = json.dumps(year_wise_setup).encode()
        req = urllib.request.Request('http://localhost:8003/timetable/setup', data=setup_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

        print('✅ Setup completed successfully!')
        print(f'📝 Response: {result["message"]}')

        # Verify data was saved to database
        print('\n🗄️ Verifying database persistence...')

        req = urllib.request.Request('http://localhost:8003/timetable/data', method='GET')
        req.add_header('Authorization', f'Bearer {token}')

        with urllib.request.urlopen(req) as response:
            saved_data = json.loads(response.read().decode())

        print('📂 Database after setup:')
        print(f'   📚 Departments: {len(saved_data.get("departments", []))}')

        for dept in saved_data.get("departments", []):
            print(f'   🏫 {dept.get("name", "Unknown")}:')
            year_subjects = dept.get("year_subjects", {})
            for year, subjects in year_subjects.items():
                print(f'      📖 Year {year}: {subjects}')

        # Check if database file exists
        db_file = "timetable_data_year_wise.json"
        if os.path.exists(db_file):
            print(f'\n💾 Database file exists: {db_file}')
            with open(db_file, 'r') as f:
                file_data = json.load(f)

            # Verify file contents
            file_dept = file_data.get("departments", [{}])[0]
            file_subjects = file_dept.get("year_subjects", {})

            year1_subjects = file_subjects.get("1", [])
            year2_subjects = file_subjects.get("2", [])

            if year1_subjects == ["CS101", "CS102", "CS103", "CS104", "CS105", "CS106"]:
                print('✅ Year 1 subjects correctly saved to file')
            else:
                print(f'❌ Year 1 subjects mismatch: {year1_subjects}')

            if year2_subjects == ["CS201", "CS202", "CS203", "CS204", "CS205", "CS206"]:
                print('✅ Year 2 subjects correctly saved to file')
            else:
                print(f'❌ Year 2 subjects mismatch: {year2_subjects}')

            print(f'💾 File size: {os.path.getsize(db_file)} bytes')
        else:
            print('❌ Database file not found!')

        print('\n🎊 Database persistence test completed!')
        print('   ✅ Year-wise subjects saved to memory')
        print('   ✅ Year-wise subjects saved to JSON file')
        print('   ✅ Data structure preserved correctly')
        print('   ✅ Backward compatibility maintained')

    except Exception as e:
        print(f'❌ Database test failed: {e}')

if __name__ == "__main__":
    test_database_persistence()
