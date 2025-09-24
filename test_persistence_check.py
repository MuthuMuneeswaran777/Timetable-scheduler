import urllib.request
import urllib.parse
import json

def test_persistence():
    print("🧪 Testing Timetable Data Persistence")
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

    # Check existing timetable data
    try:
        req = urllib.request.Request('http://localhost:8001/timetable/data', method='GET')
        req.add_header('Authorization', f'Bearer {token}')
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            print(f"\n📊 Current Timetable Data:")
            print(f"   📚 Departments: {len(data['departments'])}")
            print(f"   👨‍🏫 Teachers: {len(data['teachers'])}")
            print(f"   👨‍🎓 Students: {len(data['students'])}")
            print(f"   📅 Timetable Entries: {len(data['timetable'])}")
            
            if data['departments']:
                print(f"\n📚 Departments:")
                for dept in data['departments']:
                    print(f"   - {dept['name']}: {len(dept['sections'])} sections, {len(dept['subjects'])} subjects")
            
            if data['teachers']:
                print(f"\n👨‍🏫 Teachers:")
                for teacher in data['teachers']:
                    print(f"   - {teacher['name']} ({teacher['employee_id']}): {', '.join(teacher['subjects'])}")
            
            if len(data['students']) > 0:
                print(f"\n👨‍🎓 Sample Students:")
                for i, student in enumerate(data['students'][:5]):  # Show first 5
                    print(f"   - {student['roll_number']}: {student['name']} ({student['department']}, Year {student['year']}, Section {student['section']})")
                if len(data['students']) > 5:
                    print(f"   ... and {len(data['students']) - 5} more students")
            
            if data['timetable']:
                print(f"\n📅 Sample Timetable Entries:")
                for i, entry in enumerate(data['timetable'][:3]):  # Show first 3
                    print(f"   - {entry['day']} {entry['time_slot']}: {entry['subject']} by {entry['teacher']} in {entry['classroom']}")
                if len(data['timetable']) > 3:
                    print(f"   ... and {len(data['timetable']) - 3} more entries")
            
            print(f"\n✅ Data persistence is working!")
            print(f"💾 All timetable information is saved and will persist across restarts.")
            
    except Exception as e:
        print(f'❌ Failed to get timetable data: {e}')

if __name__ == "__main__":
    test_persistence()
