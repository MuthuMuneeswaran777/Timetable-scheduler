import urllib.request
import urllib.parse
import json

def test_force_free_periods():
    print("🧪 Force Free Periods Test")
    print("=" * 35)

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

    # Setup with many subjects to force free periods
    # With 10 subjects, max 5 per week = max 50 subjects per week
    # With 5 days * 6 slots = 30 slots total
    # This should force some free periods
    timetable_setup = {
        "departments": [
            {
                "name": "Computer Science",
                "classes": [{"name": "CS-101", "capacity": 60}],
                "labs": [{"name": "CS-Lab-1", "capacity": 30}],
                "years": 1,
                "sections": [{"name": "A", "student_count": 60}],
                "subjects": [f"CS-{i:03d}" for i in range(1, 11)]  # 10 subjects
            }
        ],
        "teachers": [
            {
                "name": "Dr. Alice",
                "employee_id": "CS001",
                "subjects": [f"CS-{i:03d}" for i in range(1, 6)],  # Can teach 5 subjects
                "department": "Computer Science"
            },
            {
                "name": "Prof. Bob",
                "employee_id": "CS002",
                "subjects": [f"CS-{i:03d}" for i in range(6, 11)],  # Can teach other 5 subjects
                "department": "Computer Science"
            }
        ]
    }

    try:
        setup_data = json.dumps(timetable_setup).encode()
        req = urllib.request.Request('http://localhost:8001/timetable/setup', data=setup_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {token}')
        urllib.request.urlopen(req)
        print('✅ Timetable setup complete')
        print('📚 10 subjects, 2 teachers (5 subjects each)')
        print('📅 5 days × 6 slots = 30 total slots')
        print('📊 Max 5 periods per subject per week')
        print('👨‍🏫 Max 4 periods per teacher per day')
        print('⚠️  Should generate some free periods')
    except Exception as e:
        print(f'❌ Setup failed: {e}')
        return

    # Generate timetable
    try:
        req = urllib.request.Request('http://localhost:8001/timetable/generate', method='POST')
        req.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            timetable = result['timetable']
            print('✅ Timetable generated')

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

            print(f'\n📊 Results Analysis:')
            print(f'   📝 Total entries: {len(timetable)}')
            print(f'   ✅ Scheduled periods: {scheduled}')
            print(f'   🆓 Free periods: {free}')

            # Check subject constraints
            subject_violations = 0
            for subject, count in subject_counts.items():
                if count > 5:
                    print(f'   ❌ Subject violation: {subject} has {count} periods (max 5)')
                    subject_violations += 1

            if subject_violations == 0:
                print('   ✅ Subject constraints: PASSED')

            # Check teacher constraints
            teacher_violations = 0
            for teacher, days in teacher_daily_counts.items():
                for day, count in days.items():
                    if count > 4:
                        print(f'   ❌ Teacher violation: {teacher} has {count} periods on {day} (max 4)')
                        teacher_violations += 1

            if teacher_violations == 0:
                print('   ✅ Teacher constraints: PASSED')

            if subject_violations == 0 and teacher_violations == 0:
                print('\n🎉 All constraints working correctly!')
                if free > 0:
                    print(f'   📊 Generated {free} free periods as expected')
                else:
                    print('   ⚠️  No free periods generated - all slots filled within constraints')

    except Exception as e:
        print(f'❌ Generation failed: {e}')

if __name__ == "__main__":
    test_force_free_periods()
