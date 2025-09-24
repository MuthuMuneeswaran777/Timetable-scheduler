#!/usr/bin/env python3
"""
Test if the required data exists for timetable generation
"""

import sqlite3
import os

def test_scheduler_data():
    """Test if required data exists for timetable generation"""
    db_path = os.path.join("backend", "dev.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check batches
        cursor.execute("SELECT COUNT(*) FROM batches")
        batch_count = cursor.fetchone()[0]
        print(f"Batches: {batch_count}")
        
        if batch_count > 0:
            cursor.execute("SELECT batch_id, batch_name FROM batches LIMIT 5")
            batches = cursor.fetchall()
            for batch in batches:
                print(f"  - Batch {batch[0]}: {batch[1]}")
        
        # Check subjects
        cursor.execute("SELECT COUNT(*) FROM subjects")
        subject_count = cursor.fetchone()[0]
        print(f"Subjects: {subject_count}")
        
        if subject_count > 0:
            cursor.execute("SELECT subject_id, subject_name FROM subjects LIMIT 5")
            subjects = cursor.fetchall()
            for subject in subjects:
                print(f"  - Subject {subject[0]}: {subject[1]}")
        
        # Check teachers
        cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cursor.fetchone()[0]
        print(f"Teachers: {teacher_count}")
        
        if teacher_count > 0:
            cursor.execute("SELECT teacher_id, teacher_name FROM teachers LIMIT 5")
            teachers = cursor.fetchall()
            for teacher in teachers:
                print(f"  - Teacher {teacher[0]}: {teacher[1]}")
        
        # Check rooms
        cursor.execute("SELECT COUNT(*) FROM rooms")
        room_count = cursor.fetchone()[0]
        print(f"Rooms: {room_count}")
        
        if room_count > 0:
            cursor.execute("SELECT room_id, room_name FROM rooms LIMIT 5")
            rooms = cursor.fetchall()
            for room in rooms:
                print(f"  - Room {room[0]}: {room[1]}")
        
        # Check subject offerings
        cursor.execute("SELECT COUNT(*) FROM subject_offerings")
        offering_count = cursor.fetchone()[0]
        print(f"Subject Offerings: {offering_count}")
        
        if offering_count > 0:
            cursor.execute("""
                SELECT so.offering_id, s.subject_name, t.teacher_name, b.batch_name, so.sessions_per_week
                FROM subject_offerings so
                JOIN subjects s ON so.subject_id = s.subject_id
                JOIN teachers t ON so.teacher_id = t.teacher_id
                JOIN batches b ON so.batch_id = b.batch_id
                LIMIT 5
            """)
            offerings = cursor.fetchall()
            for offering in offerings:
                print(f"  - Offering {offering[0]}: {offering[1]} by {offering[2]} for {offering[3]} ({offering[4]} sessions/week)")
        
        conn.close()
        
        # Summary
        print(f"\n📊 Data Summary:")
        print(f"  - Batches: {batch_count}")
        print(f"  - Subjects: {subject_count}")
        print(f"  - Teachers: {teacher_count}")
        print(f"  - Rooms: {room_count}")
        print(f"  - Subject Offerings: {offering_count}")
        
        if all([batch_count > 0, subject_count > 0, teacher_count > 0, room_count > 0, offering_count > 0]):
            print("✅ All required data exists for timetable generation!")
        else:
            print("❌ Missing required data for timetable generation!")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    test_scheduler_data()
