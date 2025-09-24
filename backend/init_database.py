#!/usr/bin/env python3
"""
Initialize the database with required tables and sample data
"""

import os
import sys

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Base, Batch, Teacher, Subject, Room, SubjectOffering, DayOfWeek

def init_database():
    """Initialize database with tables and sample data"""
    
    # Create database engine
    db_path = os.path.join(os.path.dirname(__file__), "dev.db")
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if all required tables have data
        batch_count = db.query(Batch).count()
        teacher_count = db.query(Teacher).count()
        subject_count = db.query(Subject).count()
        offering_count = db.query(SubjectOffering).count()
        
        if all([batch_count > 0, teacher_count > 0, subject_count > 0, offering_count > 0]):
            print("Database already has all required data. Skipping initialization.")
            return
        
        print("Database is missing some required data. Initializing...")
        
        print("Adding sample data...")
        
        # Add batches
        batches = [
            Batch(batch_name="CSE-3A", department="Computer Science", sem="3", academic_year="2024-25"),
            Batch(batch_name="CSE-3B", department="Computer Science", sem="3", academic_year="2024-25"),
            Batch(batch_name="ECE-3A", department="Electronics", sem="3", academic_year="2024-25"),
        ]
        for batch in batches:
            db.add(batch)
        db.commit()
        print(f"Added {len(batches)} batches")
        
        # Add teachers
        teachers = [
            Teacher(teacher_name="Dr. Sharma", email="sharma@college.edu", max_sessions_per_day=4, max_sessions_per_week=20),
            Teacher(teacher_name="Prof. Kumar", email="kumar@college.edu", max_sessions_per_day=3, max_sessions_per_week=15),
            Teacher(teacher_name="Dr. Singh", email="singh@college.edu", max_sessions_per_day=4, max_sessions_per_week=18),
            Teacher(teacher_name="Prof. Gupta", email="gupta@college.edu", max_sessions_per_day=3, max_sessions_per_week=16),
            Teacher(teacher_name="Dr. Patel", email="patel@college.edu", max_sessions_per_day=4, max_sessions_per_week=20),
        ]
        for teacher in teachers:
            db.add(teacher)
        db.commit()
        print(f"Added {len(teachers)} teachers")
        
        # Add subjects
        subjects = [
            Subject(subject_name="Data Structures", teacher_id=1, sessions_per_week=4, is_lab=False),
            Subject(subject_name="Database Management", teacher_id=2, sessions_per_week=3, is_lab=False),
            Subject(subject_name="Computer Networks", teacher_id=3, sessions_per_week=3, is_lab=False),
            Subject(subject_name="Operating Systems", teacher_id=4, sessions_per_week=4, is_lab=False),
            Subject(subject_name="Software Engineering", teacher_id=5, sessions_per_week=3, is_lab=False),
            Subject(subject_name="DS Lab", teacher_id=1, sessions_per_week=2, is_lab=True),
            Subject(subject_name="DBMS Lab", teacher_id=2, sessions_per_week=2, is_lab=True),
            Subject(subject_name="Networks Lab", teacher_id=3, sessions_per_week=2, is_lab=True),
        ]
        for subject in subjects:
            db.add(subject)
        db.commit()
        print(f"Added {len(subjects)} subjects")
        
        # Add more rooms
        existing_rooms = db.query(Room).all()
        new_rooms = [
            Room(room_name="103", capacity=40, room_type="CLASSROOM"),
            Room(room_name="104", capacity=35, room_type="CLASSROOM"),
            Room(room_name="Lab-1", capacity=30, room_type="LAB"),
            Room(room_name="Lab-2", capacity=30, room_type="LAB"),
            Room(room_name="Lab-3", capacity=25, room_type="LAB"),
        ]
        for room in new_rooms:
            db.add(room)
        db.commit()
        print(f"Added {len(new_rooms)} new rooms (total: {len(existing_rooms) + len(new_rooms)})")
        
        # Add subject offerings for CSE-3A batch
        offerings = [
            SubjectOffering(subject_id=1, teacher_id=1, batch_id=1, sessions_per_week=4, max_sessions_per_day=2, priority=1),
            SubjectOffering(subject_id=2, teacher_id=2, batch_id=1, sessions_per_week=3, max_sessions_per_day=1, priority=2),
            SubjectOffering(subject_id=3, teacher_id=3, batch_id=1, sessions_per_week=3, max_sessions_per_day=1, priority=3),
            SubjectOffering(subject_id=4, teacher_id=4, batch_id=1, sessions_per_week=4, max_sessions_per_day=2, priority=4),
            SubjectOffering(subject_id=5, teacher_id=5, batch_id=1, sessions_per_week=3, max_sessions_per_day=1, priority=5),
            SubjectOffering(subject_id=6, teacher_id=1, batch_id=1, sessions_per_week=2, max_sessions_per_day=2, priority=6),
            SubjectOffering(subject_id=7, teacher_id=2, batch_id=1, sessions_per_week=2, max_sessions_per_day=2, priority=7),
        ]
        for offering in offerings:
            db.add(offering)
        db.commit()
        print(f"Added {len(offerings)} subject offerings")
        
        print("✅ Database initialization completed successfully!")
        
        # Print summary
        print(f"\n📊 Database Summary:")
        print(f"  - Batches: {db.query(Batch).count()}")
        print(f"  - Teachers: {db.query(Teacher).count()}")
        print(f"  - Subjects: {db.query(Subject).count()}")
        print(f"  - Rooms: {db.query(Room).count()}")
        print(f"  - Subject Offerings: {db.query(SubjectOffering).count()}")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
