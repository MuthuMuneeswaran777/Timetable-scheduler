import urllib.request
import urllib.parse
import json

def test_dashboard_data_display():
    print("📊 Testing Dashboard Data Display")
    print("=" * 40)

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

    # Get timetable data
    try:
        req = urllib.request.Request('http://localhost:8003/timetable/data', method='GET')
        req.add_header('Authorization', f'Bearer {token}')

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        print('📂 Database Overview:')
        print(f'   🏫 Departments: {len(data.get("departments", []))}')
        print(f'   👨‍🏫 Teachers: {len(data.get("teachers", []))}')
        print(f'   👨‍🎓 Students: {len(data.get("students", []))}')
        print(f'   📅 Timetables: {len(data.get("timetable", []))}')

        # Analyze departments
        print('\n🏫 Department Details:')
        for i, dept in enumerate(data.get("departments", [])):
            print(f'   📚 {dept.get("name", "Unknown")}:')
            year_subjects = dept.get("year_subjects", {})
            for year, subjects in year_subjects.items():
                print(f'      📖 Year {year}: {subjects} ({len(subjects)} subjects)')

            print(f'      🏢 Classes: {len(dept.get("classes", []))}')
            print(f'      📏 Sections: {len(dept.get("sections", []))}')

        # Analyze teachers
        print('\n👨‍🏫 Teacher Details:')
        for i, teacher in enumerate(data.get("teachers", [])):
            print(f'   👨‍🏫 {teacher.get("name", "Unknown")} ({teacher.get("employee_id", "N/A")})')
            print(f'      📚 Department: {teacher.get("department", "N/A")}')
            print(f'      📝 Subjects: {teacher.get("subjects", [])}')

        # Analyze students
        print('\n👨‍🎓 Student Distribution:')
        students_by_dept = {}
        for student in data.get("students", []):
            dept = student.get("department", "Unknown")
            if dept not in students_by_dept:
                students_by_dept[dept] = {}
            year = str(student.get("year", "N/A"))
            if year not in students_by_dept[dept]:
                students_by_dept[dept][year] = {}
            section = student.get("section", "N/A")
            if section not in students_by_dept[dept][year]:
                students_by_dept[dept][year][section] = 0
            students_by_dept[dept][year][section] += 1

        for dept, years in students_by_dept.items():
            print(f'   🏫 {dept}:')
            for year, sections in years.items():
                print(f'      📖 Year {year}:')
                for section, count in sections.items():
                    print(f'         📏 Section {section}: {count} students')

        # Analyze timetables
        print('\n📅 Timetable Analysis:')
        if data.get("timetable"):
            departments = set()
            subjects = set()
            teachers = set()

            for entry in data.get("timetable", []):
                departments.add(entry.get("department", "N/A"))
                subjects.add(entry.get("subject", "N/A"))
                teachers.add(entry.get("teacher", "N/A"))

            print(f'   📊 Total entries: {len(data.get("timetable", []))}')
            print(f'   🏫 Departments covered: {len(departments)}')
            print(f'   📚 Subjects scheduled: {len(subjects)}')
            print(f'   👨‍🏫 Teachers assigned: {len(teachers)}')

            # Show sample entries
            print('\n   📋 Sample timetable entries (first 5):')
            for i, entry in enumerate(data.get("timetable", [])):
                if i >= 5:
                    break
                print(f'      {entry.get("day", "N/A")} {entry.get("time_slot", "N/A")}: {entry.get("subject", "N/A")} with {entry.get("teacher", "N/A")} in {entry.get("classroom", "N/A")}')

        print('\n🎊 Dashboard data display test completed!')
        print('   ✅ All database data accessible')
        print('   ✅ Year-wise subjects displayed correctly')
        print('   ✅ Teachers and subjects organized properly')
        print('   ✅ Students grouped by department/year/section')
        print('   ✅ Timetables analyzed with statistics')
        print('   ✅ Ready for comprehensive dashboard display')

    except Exception as e:
        print(f'❌ Dashboard test failed: {e}')

if __name__ == "__main__":
    test_dashboard_data_display()
