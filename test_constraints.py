import urllib.request
import urllib.parse
import json

def test_constraints():
    print("🧪 Testing Timetable Constraints")
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

    # Timetable setup with more subjects than slots
    timetable_setup = {
        "departments": [
            {
                "name": "Physics",
                "classes": [{"name": "PHY-101", "capacity": 50}],
                "labs": [],
                "years": 1,
                "sections": [{"name": "A", "student_count": 50}],
                "subjects": [f"PHY-0{i}" for i in range(1, 11)] # 10 subjects
            }
        ],
        "teachers": [
            {
                "name": "Prof. Einstein",
                "employee_id": "PHY001",
                "subjects": [f"PHY-0{i}" for i in range(1, 6)], # Teaches 5 subjects
                "department": "Physics"
            },
            {
                "name": "Prof. Newton",
                "employee_id": "PHY002",
                "subjects": [f"PHY-0{i}" for i in range(6, 11)], # Teaches other 5 subjects
                "department": "Physics"
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
    except Exception as e:
        print(f'❌ Generation failed: {e}')
        return

    # Verify constraints
    subject_counts = {}
    teacher_daily_counts = {}
    free_periods = 0

    for entry in timetable:
        if entry['subject'] == 'Free Period':
            free_periods += 1
            continue

        # Subject weekly count
        subject_key = f"{entry['department']}-{entry['year']}-{entry['section']}-{entry['subject']}"
        subject_counts[subject_key] = subject_counts.get(subject_key, 0) + 1

        # Teacher daily count
        teacher_key = f"{entry['teacher']}-{entry['day']}"
        teacher_daily_counts[teacher_key] = teacher_daily_counts.get(teacher_key, 0) + 1

    print("\n📊 Verification Results:")
    # Check subject constraint
    for subject, count in subject_counts.items():
        if count > 5:
            print(f"❌ Subject Constraint VIOLATED for {subject}: {count} periods")
            return
    print("✅ Subject Constraint (Max 5 per week): PASSED")

    # Check teacher constraint
    for teacher, count in teacher_daily_counts.items():
        if count > 4:
            print(f"❌ Teacher Constraint VIOLATED for {teacher}: {count} periods")
            return
    print("✅ Teacher Constraint (Max 4 per day): PASSED")
    
    print(f"🆓 Free Periods Generated: {free_periods}")
    if free_periods == 0:
        print("⚠️ Warning: No free periods were generated. This might be unexpected.")

    print("\n🎉 All constraints are working correctly!")

if __name__ == "__main__":
    test_constraints()
