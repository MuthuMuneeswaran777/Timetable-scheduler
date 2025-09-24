#!/usr/bin/env python3
"""
Add sample data through the API
"""

import requests
import json

def add_sample_data():
    """Add sample data through the API"""
    base_url = "http://localhost:8000"
    
    try:
        # Add teachers
        print("Adding teachers...")
        teachers = [
            {"teacher_name": "Dr. Sharma", "email": "sharma@college.edu", "max_sessions_per_day": 4, "max_sessions_per_week": 20},
            {"teacher_name": "Prof. Kumar", "email": "kumar@college.edu", "max_sessions_per_day": 3, "max_sessions_per_week": 15},
            {"teacher_name": "Dr. Singh", "email": "singh@college.edu", "max_sessions_per_day": 4, "max_sessions_per_week": 18},
            {"teacher_name": "Prof. Gupta", "email": "gupta@college.edu", "max_sessions_per_day": 3, "max_sessions_per_week": 16},
            {"teacher_name": "Dr. Patel", "email": "patel@college.edu", "max_sessions_per_day": 4, "max_sessions_per_week": 20},
        ]
        
        for teacher in teachers:
            response = requests.post(f"{base_url}/data/teachers", json=teacher)
            if response.status_code == 200:
                print(f"  ✅ Added teacher: {teacher['teacher_name']}")
            else:
                print(f"  ❌ Failed to add teacher {teacher['teacher_name']}: {response.text}")
        
        # Add subjects
        print("\nAdding subjects...")
        subjects = [
            {"subject_name": "Data Structures", "teacher_id": 1, "sessions_per_week": 4, "is_lab": False},
            {"subject_name": "Database Management", "teacher_id": 2, "sessions_per_week": 3, "is_lab": False},
            {"subject_name": "Computer Networks", "teacher_id": 3, "sessions_per_week": 3, "is_lab": False},
            {"subject_name": "Operating Systems", "teacher_id": 4, "sessions_per_week": 4, "is_lab": False},
            {"subject_name": "Software Engineering", "teacher_id": 5, "sessions_per_week": 3, "is_lab": False},
            {"subject_name": "DS Lab", "teacher_id": 1, "sessions_per_week": 2, "is_lab": True},
            {"subject_name": "DBMS Lab", "teacher_id": 2, "sessions_per_week": 2, "is_lab": True},
        ]
        
        for subject in subjects:
            response = requests.post(f"{base_url}/data/subjects", json=subject)
            if response.status_code == 200:
                print(f"  ✅ Added subject: {subject['subject_name']}")
            else:
                print(f"  ❌ Failed to add subject {subject['subject_name']}: {response.text}")
        
        # Add more rooms
        print("\nAdding rooms...")
        rooms = [
            {"room_name": "103", "capacity": 40, "room_type": "CLASSROOM", "assigned_batch_id": None},
            {"room_name": "104", "capacity": 35, "room_type": "CLASSROOM", "assigned_batch_id": None},
            {"room_name": "Lab-1", "capacity": 30, "room_type": "LAB", "assigned_batch_id": None},
            {"room_name": "Lab-2", "capacity": 30, "room_type": "LAB", "assigned_batch_id": None},
        ]
        
        for room in rooms:
            response = requests.post(f"{base_url}/data/rooms", json=room)
            if response.status_code == 200:
                print(f"  ✅ Added room: {room['room_name']}")
            else:
                print(f"  ❌ Failed to add room {room['room_name']}: {response.text}")
        
        # Add subject offerings
        print("\nAdding subject offerings...")
        offerings = [
            {"subject_id": 1, "teacher_id": 1, "batch_id": 1, "sessions_per_week": 4, "max_sessions_per_day": 2, "priority": 1},
            {"subject_id": 2, "teacher_id": 2, "batch_id": 1, "sessions_per_week": 3, "max_sessions_per_day": 1, "priority": 2},
            {"subject_id": 3, "teacher_id": 3, "batch_id": 1, "sessions_per_week": 3, "max_sessions_per_day": 1, "priority": 3},
            {"subject_id": 4, "teacher_id": 4, "batch_id": 1, "sessions_per_week": 4, "max_sessions_per_day": 2, "priority": 4},
            {"subject_id": 5, "teacher_id": 5, "batch_id": 1, "sessions_per_week": 3, "max_sessions_per_day": 1, "priority": 5},
            {"subject_id": 6, "teacher_id": 1, "batch_id": 1, "sessions_per_week": 2, "max_sessions_per_day": 2, "priority": 6},
            {"subject_id": 7, "teacher_id": 2, "batch_id": 1, "sessions_per_week": 2, "max_sessions_per_day": 2, "priority": 7},
        ]
        
        for offering in offerings:
            response = requests.post(f"{base_url}/data/subject_offerings", json=offering)
            if response.status_code == 200:
                print(f"  ✅ Added offering: Subject {offering['subject_id']} by Teacher {offering['teacher_id']} for Batch {offering['batch_id']}")
            else:
                print(f"  ❌ Failed to add offering: {response.text}")
        
        print("\n🎉 Sample data added successfully!")
        
    except Exception as e:
        print(f"❌ Failed to add sample data: {e}")

if __name__ == "__main__":
    add_sample_data()
