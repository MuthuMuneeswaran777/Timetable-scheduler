import urllib.request
import urllib.parse
import json
import time

def test_or_tools_optimization():
    print("🧪 Testing OR-Tools CP-SAT Optimization")
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

    # Setup with realistic data
    timetable_setup = {
        "departments": [
            {
                "name": "Computer Science",
                "classes": [
                    {"name": "CS-Lab-101", "capacity": 60},
                    {"name": "CS-Lab-102", "capacity": 60},
                    {"name": "CS-Class-201", "capacity": 50}
                ],
                "labs": [
                    {"name": "CS-Lab-101", "capacity": 30},
                    {"name": "CS-Lab-102", "capacity": 30}
                ],
                "years": 1,
                "sections": [
                    {"name": "A", "student_count": 60},
                    {"name": "B", "student_count": 60}
                ],
                "subjects": ["CS101", "CS102", "CS103", "CS104", "CS105", "CS106", "CS107", "CS108"]
            },
            {
                "name": "Mathematics",
                "classes": [
                    {"name": "Math-101", "capacity": 50},
                    {"name": "Math-102", "capacity": 50}
                ],
                "labs": [],
                "years": 1,
                "sections": [
                    {"name": "A", "student_count": 50},
                    {"name": "B", "student_count": 50}
                ],
                "subjects": ["MATH101", "MATH102", "MATH103", "MATH104", "MATH105"]
            }
        ],
        "teachers": [
            {
                "name": "Dr. Alice Johnson",
                "employee_id": "CS001",
                "subjects": ["CS101", "CS102", "CS103"],
                "department": "Computer Science"
            },
            {
                "name": "Prof. Bob Smith",
                "employee_id": "CS002",
                "subjects": ["CS104", "CS105", "CS106"],
                "department": "Computer Science"
            },
            {
                "name": "Dr. Charlie Brown",
                "employee_id": "CS003",
                "subjects": ["CS107", "CS108"],
                "department": "Computer Science"
            },
            {
                "name": "Prof. Diana Wilson",
                "employee_id": "MATH001",
                "subjects": ["MATH101", "MATH102", "MATH103"],
                "department": "Mathematics"
            },
            {
                "name": "Dr. Edward Davis",
                "employee_id": "MATH002",
                "subjects": ["MATH104", "MATH105"],
                "department": "Mathematics"
            }
        ]
    }

    try:
        setup_data = json.dumps(timetable_setup).encode()
        req = urllib.request.Request('http://localhost:8002/timetable/setup', data=setup_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')
        urllib.request.urlopen(req)
        print('✅ Timetable setup complete')
        print('📚 Departments: 2 (CS, Math)')
        print('👨‍🏫 Teachers: 5 total')
        print('📝 Subjects: 13 total')
        print('📅 5 days × 6 slots = 30 slots per class')
        print('⚡ OR-Tools CP-SAT optimization starting...')
    except Exception as e:
        print(f'❌ Setup failed: {e}')
        return

    # Generate timetable with OR-Tools
    start_time = time.time()
    try:
        req = urllib.request.Request('http://localhost:8002/timetable/generate', method='POST')
        req.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            timetable = result['timetable']
            generation_time = time.time() - start_time

            print('✅ OR-Tools CP-SAT timetable generated!')
            print(f'⏱️ Generation time: {generation_time:.2f} seconds')
            print(f'📊 Total entries: {len(timetable)}')

            # Analyze results
            scheduled = 0
            free = 0
            subject_counts = {}
            teacher_daily_counts = {}

            for entry in timetable:
                if entry['subject'] == 'Free Period':
                    free += 1
                else:
                    scheduled += 1
                    # Count subject usage
                    subject_key = f"{entry['department']}-{entry['year']}-{entry['section']}-{entry['subject']}"
                    subject_counts[subject_key] = subject_counts.get(subject_key, 0) + 1

                    # Count teacher daily usage
                    teacher_key = f"{entry['teacher']}-{entry['day']}"
                    if entry['teacher'] not in teacher_daily_counts:
                        teacher_daily_counts[entry['teacher']] = {}
                    teacher_daily_counts[entry['teacher']][teacher_key] = teacher_daily_counts[entry['teacher']].get(teacher_key, 0) + 1

            print(f'✅ Scheduled periods: {scheduled}')
            print(f'🆓 Free periods: {free}')

            # Check constraints
            subject_violations = 0
            for subject, count in subject_counts.items():
                if count > 5:
                    print(f'❌ Subject violation: {subject} has {count} periods (max 5)')
                    subject_violations += 1

            teacher_violations = 0
            for teacher, days in teacher_daily_counts.items():
                for day, count in days.items():
                    if count > 4:
                        print(f'❌ Teacher violation: {teacher} has {count} periods on {day} (max 4)')
                        teacher_violations += 1

            if subject_violations == 0 and teacher_violations == 0:
                print('✅ All constraints satisfied!')
                print('🎯 OR-Tools CP-SAT optimization successful!')
            else:
                print('⚠️ Some constraint violations detected')

    except Exception as e:
        print(f'❌ Generation failed: {e}')

if __name__ == "__main__":
    test_or_tools_optimization()
