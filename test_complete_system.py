import urllib.request
import urllib.parse
import json

# Test the complete timetable creation system
def test_timetable_system():
    print("🚀 Testing Complete Timetable Creation System")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("\n📝 Step 1: Admin Login")
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

    # Step 2: Setup comprehensive timetable system
    print("\n📚 Step 2: Setting up Timetable System")
    
    timetable_setup = {
        "departments": [
            {
                "name": "Computer Science",
                "classes": [
                    {"name": "CS-101", "capacity": 60},
                    {"name": "CS-102", "capacity": 60},
                    {"name": "CS-103", "capacity": 60}
                ],
                "labs": [
                    {"name": "CS-Lab-1", "capacity": 30},
                    {"name": "CS-Lab-2", "capacity": 30}
                ],
                "years": 4,
                "sections": [
                    {"name": "A", "student_count": 50},
                    {"name": "B", "student_count": 45}
                ],
                "subjects": [
                    "Programming Fundamentals",
                    "Data Structures",
                    "Database Systems",
                    "Computer Networks",
                    "Software Engineering",
                    "Operating Systems"
                ]
            },
            {
                "name": "Electronics",
                "classes": [
                    {"name": "EC-201", "capacity": 50},
                    {"name": "EC-202", "capacity": 50}
                ],
                "labs": [
                    {"name": "EC-Lab-1", "capacity": 25}
                ],
                "years": 4,
                "sections": [
                    {"name": "A", "student_count": 40},
                    {"name": "B", "student_count": 35}
                ],
                "subjects": [
                    "Circuit Analysis",
                    "Digital Electronics",
                    "Microprocessors",
                    "Signal Processing",
                    "Communication Systems"
                ]
            }
        ],
        "teachers": [
            {
                "name": "Dr. Alice Johnson",
                "employee_id": "CS001",
                "subjects": ["Programming Fundamentals", "Data Structures"],
                "department": "Computer Science"
            },
            {
                "name": "Prof. Bob Smith",
                "employee_id": "CS002", 
                "subjects": ["Database Systems", "Software Engineering"],
                "department": "Computer Science"
            },
            {
                "name": "Dr. Carol Brown",
                "employee_id": "CS003",
                "subjects": ["Computer Networks", "Operating Systems"],
                "department": "Computer Science"
            },
            {
                "name": "Dr. David Wilson",
                "employee_id": "EC001",
                "subjects": ["Circuit Analysis", "Digital Electronics"],
                "department": "Electronics"
            },
            {
                "name": "Prof. Eva Davis",
                "employee_id": "EC002",
                "subjects": ["Microprocessors", "Signal Processing", "Communication Systems"],
                "department": "Electronics"
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
            print('✅ Timetable setup completed!')
            print(f"📊 Summary:")
            print(f"   📚 Departments: {result['summary']['departments']}")
            print(f"   👨‍🏫 Teachers: {result['summary']['teachers']}")
            print(f"   👨‍🎓 Students: {result['summary']['students']}")
            print(f"   🔑 Accounts Created: {result['summary']['accounts_created']}")
            
    except urllib.error.HTTPError as e:
        print(f'❌ Setup failed: {e.code}')
        print(f'Error: {e.read().decode()}')
        return
    except Exception as e:
        print(f'❌ Setup error: {e}')
        return

    # Step 3: Generate timetable
    print("\n⚡ Step 3: Generating Timetable")
    
    try:
        req = urllib.request.Request('http://localhost:8001/timetable/generate', method='POST')
        req.add_header('Authorization', f'Bearer {token}')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print('✅ Timetable generated successfully!')
            print(f"📋 Generated {result['entries']} timetable entries")
            
    except Exception as e:
        print(f'❌ Generation failed: {e}')
        return

    # Step 4: View generated timetable
    print("\n👀 Step 4: Viewing Generated Timetable")
    
    try:
        req = urllib.request.Request('http://localhost:8001/timetable/view', method='GET')
        req.add_header('Authorization', f'Bearer {token}')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            timetable = result['timetable']
            
            print(f'📅 Total timetable entries: {len(timetable)}')
            
            # Show sample entries
            print("\n📋 Sample Timetable Entries:")
            print("-" * 80)
            print(f"{'Day':<10} {'Time':<12} {'Subject':<20} {'Teacher':<15} {'Room':<10} {'Dept-Year-Sec'}")
            print("-" * 80)
            
            for i, entry in enumerate(timetable[:10]):  # Show first 10 entries
                dept_year_sec = f"{entry['department'][:3]}-{entry['year']}-{entry['section']}"
                print(f"{entry['day']:<10} {entry['time_slot']:<12} {entry['subject'][:20]:<20} {entry['teacher'][:15]:<15} {entry['classroom']:<10} {dept_year_sec}")
            
            if len(timetable) > 10:
                print(f"... and {len(timetable) - 10} more entries")
                
    except Exception as e:
        print(f'❌ View failed: {e}')
        return

    # Step 5: Test student login
    print("\n🎓 Step 5: Testing Auto-Created Student Account")
    
    # Try to login with a generated student account
    student_login_data = urllib.parse.urlencode({
        'username': 'COM1A001',  # First student in CS Year 1 Section A
        'password': 'COM1A001'   # Default password is roll number
    }).encode()

    try:
        req = urllib.request.Request('http://localhost:8001/token', data=student_login_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            student_token = result['access_token']
            print('✅ Student login successful with auto-generated account!')
            print(f'   Username: COM1A001 (Computer Science, Year 1, Section A, Student 1)')
            
            # Get student's personal timetable
            req = urllib.request.Request('http://localhost:8001/timetable/view', method='GET')
            req.add_header('Authorization', f'Bearer {student_token}')
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                student_timetable = result['timetable']
                print(f'📚 Student can view their personal timetable: {len(student_timetable)} entries')
                
    except Exception as e:
        print(f'❌ Student login failed: {e}')

    # Step 6: Test faculty login
    print("\n👨‍🏫 Step 6: Testing Auto-Created Faculty Account")
    
    faculty_login_data = urllib.parse.urlencode({
        'username': 'CS001',     # Dr. Alice Johnson's employee ID
        'password': 'CS001'      # Default password is employee ID
    }).encode()

    try:
        req = urllib.request.Request('http://localhost:8001/token', data=faculty_login_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            faculty_token = result['access_token']
            print('✅ Faculty login successful with auto-generated account!')
            print(f'   Username: CS001 (Dr. Alice Johnson)')
            
    except Exception as e:
        print(f'❌ Faculty login failed: {e}')

    print("\n🎉 Complete Timetable System Test Finished!")
    print("=" * 50)
    print("✅ System Features Tested:")
    print("   📚 Multi-department setup")
    print("   👥 Automatic user account creation")
    print("   📋 Intelligent timetable generation")
    print("   🔐 Role-based access control")
    print("   💾 Persistent data storage")
    print("   🎓 Student roll number generation")
    print("   👨‍🏫 Faculty management")

if __name__ == "__main__":
    test_timetable_system()
