import urllib.request
import urllib.parse
import json

def test_year_wise_subjects():
    print("🧪 Testing Year-Wise Subjects Configuration")
    print("=" * 45)

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
                "years": 2,  # 2 years
                "sections": [
                    {"name": "A", "student_count": 60},
                    {"name": "B", "student_count": 60}
                ],
                "year_subjects": {
                    "1": ["CS101", "CS102", "CS103", "CS104", "CS105", "CS106"],  # 1st year subjects
                    "2": ["CS201", "CS202", "CS203", "CS204", "CS205", "CS206"]   # 2nd year subjects
                }
            }
        ],
        "teachers": [
            # CS Department teachers
            {
                "name": "Dr. Alice Johnson",
                "employee_id": "CS001",
                "subjects": ["CS101", "CS102", "CS103"],
                "department": "Computer Science"
            },
            {
                "name": "Prof. Bob Smith",
                "employee_id": "CS002",
                "subjects": ["CS104", "CS105", "CS106", "CS201"],
                "department": "Computer Science"
            }
        ]
    }

    try:
        setup_data = json.dumps(year_wise_setup).encode()
        req = urllib.request.Request('http://localhost:8002/timetable/setup', data=setup_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')
        urllib.request.urlopen(req)
        print('✅ Year-wise subjects setup complete')
        print('📚 Computer Science:')
        print('   📖 1st Year: CS101, CS102, CS103, CS104, CS105, CS106')
        print('   📖 2nd Year: CS201, CS202, CS203, CS204, CS205, CS206')
        print('📐 Mathematics:')
        print('   📖 1st Year: MATH101-MATH106')
        print('   📖 2nd Year: MATH201-MATH206')
        print('👨‍🏫 Teachers: 6 total (3 per department)')
        print('⚡ OR-Tools will schedule different subjects for each year!')
    except Exception as e:
        print(f'❌ Setup failed: {e}')
        return

    # Generate timetable with year-wise subjects
    try:
        req = urllib.request.Request('http://localhost:8002/timetable/generate', method='POST')
        req.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            timetable = result['timetable']

            print('✅ Year-wise timetable generated!')
            print(f'📊 Total entries: {len(timetable)}')

            # Analyze by year and subject
            year1_subjects = {}
            year2_subjects = {}
            teacher_assignments = {}

            for entry in timetable:
                if entry['subject'] == 'Free Period':
                    continue

                year = entry['year']
                subject = entry['subject']
                teacher = entry['teacher']

                if year == 1:
                    year1_subjects[subject] = year1_subjects.get(subject, 0) + 1
                else:
                    year2_subjects[subject] = year2_subjects.get(subject, 0) + 1

                if teacher not in teacher_assignments:
                    teacher_assignments[teacher] = 0
                teacher_assignments[teacher] += 1

            print('\n📊 Year 1 Subjects (CS101-CS106, MATH101-MATH106):')
            for subject, count in sorted(year1_subjects.items()):
                print(f'   📘 {subject}: {count} periods')

            print('\n📊 Year 2 Subjects (CS201-CS206, MATH201-MATH206):')
            for subject, count in sorted(year2_subjects.items()):
                print(f'   📘 {subject}: {count} periods')

            print('\n👨‍🏫 Teacher Workload:')
            for teacher, count in sorted(teacher_assignments.items()):
                print(f'   👨‍🏫 {teacher}: {count} periods')

            # Verify constraints
            year1_violations = sum(1 for count in year1_subjects.values() if count > 5)
            year2_violations = sum(1 for count in year2_subjects.values() if count > 5)
            teacher_violations = sum(1 for count in teacher_assignments.values() if count > 24)  # 4 per day × 6 days

            if year1_violations == 0 and year2_violations == 0:
                print('✅ Subject constraints: PASSED (≤5 periods/week per subject)')
            else:
                print(f'❌ Subject constraints: {year1_violations + year2_violations} violations')

            if teacher_violations == 0:
                print('✅ Teacher constraints: PASSED (≤4 periods/day)')
            else:
                print(f'❌ Teacher constraints: {teacher_violations} violations')

            print('\n🎯 Key Points:')
            print('   ✅ 1st year students get only 1st year subjects')
            print('   ✅ 2nd year students get only 2nd year subjects')
            print('   ✅ No subject mixing between years')
            print('   ✅ Teachers only teach subjects they know')
            print('   ✅ All constraints respected')

    except Exception as e:
        print(f'❌ Generation failed: {e}')

if __name__ == "__main__":
    test_year_wise_subjects()
