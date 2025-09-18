"""
Test script to demonstrate lab conflict resolution
This script creates sample data and generates timetables for multiple batches
to show how the scheduler handles lab teacher conflicts
"""

from sqlalchemy.orm import Session
from backend.database import get_db, engine
from backend.models import *
from backend.scheduler import generate_timetable

def create_sample_data(db: Session):
    """Create sample data for testing lab conflicts"""
    
    # Clear existing data
    db.query(TimetableEntry).delete()
    db.query(Timetable).delete()
    db.query(SubjectOffering).delete()
    db.query(Subject).delete()
    db.query(Teacher).delete()
    db.query(Room).delete()
    db.query(Batch).delete()
    db.commit()
    
    # Create batches
    batch1 = Batch(batch_name="CSE-A", department="Computer Science", sem="5", academic_year="2024-25")
    batch2 = Batch(batch_name="CSE-B", department="Computer Science", sem="5", academic_year="2024-25")
    db.add_all([batch1, batch2])
    db.commit()
    db.refresh(batch1)
    db.refresh(batch2)
    
    # Create teachers
    teacher1 = Teacher(teacher_name="Dr. Smith", email="smith@college.edu", max_sessions_per_day=6)
    teacher2 = Teacher(teacher_name="Prof. Johnson", email="johnson@college.edu", max_sessions_per_day=6)
    teacher3 = Teacher(teacher_name="Dr. Wilson", email="wilson@college.edu", max_sessions_per_day=6)  # Lab teacher
    db.add_all([teacher1, teacher2, teacher3])
    db.commit()
    db.refresh(teacher1)
    db.refresh(teacher2)
    db.refresh(teacher3)
    
    # Create rooms
    room1 = Room(room_name="Room-101", capacity=60, room_type="CLASSROOM")
    room2 = Room(room_name="Room-102", capacity=60, room_type="CLASSROOM")
    lab1 = Room(room_name="CS-Lab-1", capacity=30, room_type="LAB")
    lab2 = Room(room_name="CS-Lab-2", capacity=30, room_type="LAB")
    db.add_all([room1, room2, lab1, lab2])
    db.commit()
    
    # Create subjects
    math = Subject(subject_name="Mathematics", teacher_id=teacher1.teacher_id, sessions_per_week=5, is_lab=False)
    physics = Subject(subject_name="Physics", teacher_id=teacher2.teacher_id, sessions_per_week=4, is_lab=False)
    cs_lab = Subject(subject_name="Computer Science Lab", teacher_id=teacher3.teacher_id, sessions_per_week=1, is_lab=True, lab_duration=3)
    db.add_all([math, physics, cs_lab])
    db.commit()
    db.refresh(math)
    db.refresh(physics)
    db.refresh(cs_lab)
    
    # Create subject offerings for both batches (same teacher for CS Lab)
    offerings = [
        # Batch 1 offerings
        SubjectOffering(subject_id=math.subject_id, teacher_id=teacher1.teacher_id, batch_id=batch1.batch_id, sessions_per_week=5, priority=1),
        SubjectOffering(subject_id=physics.subject_id, teacher_id=teacher2.teacher_id, batch_id=batch1.batch_id, sessions_per_week=4, priority=2),
        SubjectOffering(subject_id=cs_lab.subject_id, teacher_id=teacher3.teacher_id, batch_id=batch1.batch_id, sessions_per_week=1, priority=3),
        
        # Batch 2 offerings (same CS Lab teacher - this will cause conflict)
        SubjectOffering(subject_id=math.subject_id, teacher_id=teacher1.teacher_id, batch_id=batch2.batch_id, sessions_per_week=5, priority=1),
        SubjectOffering(subject_id=physics.subject_id, teacher_id=teacher2.teacher_id, batch_id=batch2.batch_id, sessions_per_week=4, priority=2),
        SubjectOffering(subject_id=cs_lab.subject_id, teacher_id=teacher3.teacher_id, batch_id=batch2.batch_id, sessions_per_week=1, priority=3),
    ]
    
    db.add_all(offerings)
    db.commit()
    
    print("✅ Sample data created successfully!")
    print(f"   - Batches: {batch1.batch_name}, {batch2.batch_name}")
    print(f"   - Teachers: {teacher1.teacher_name}, {teacher2.teacher_name}, {teacher3.teacher_name}")
    print(f"   - Lab teacher {teacher3.teacher_name} is assigned to both batches")
    
    return batch1.batch_id, batch2.batch_id

def test_lab_conflict_resolution():
    """Test the lab conflict resolution functionality"""
    
    print("🧪 Testing Lab Conflict Resolution")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create sample data
        batch1_id, batch2_id = create_sample_data(db)
        
        print(f"\n📅 Generating timetable for Batch 1 (ID: {batch1_id})")
        print("-" * 40)
        tt1 = generate_timetable(db, batch1_id)
        
        print(f"\n📅 Generating timetable for Batch 2 (ID: {batch2_id})")
        print("-" * 40)
        tt2 = generate_timetable(db, batch2_id)
        
        print(f"\n📊 Results Summary:")
        print(f"   - Batch 1 timetable ID: {tt1.timetable_id}")
        print(f"   - Batch 2 timetable ID: {tt2.timetable_id}")
        
        # Check if both batches got their lab sessions
        batch1_entries = db.query(TimetableEntry).filter(TimetableEntry.timetable_id == tt1.timetable_id, TimetableEntry.is_lab_session == True).all()
        batch2_entries = db.query(TimetableEntry).filter(TimetableEntry.timetable_id == tt2.timetable_id, TimetableEntry.is_lab_session == True).all()
        
        print(f"\n🔬 Lab Session Analysis:")
        if batch1_entries:
            lab_day = batch1_entries[0].day_of_week.value
            lab_periods = [e.period_number for e in batch1_entries]
            lab_periods.sort()
            print(f"   - Batch 1: Lab scheduled on {lab_day}, periods {lab_periods}")
        else:
            print(f"   - Batch 1: ❌ No lab sessions scheduled")
            
        if batch2_entries:
            lab_day = batch2_entries[0].day_of_week.value
            lab_periods = [e.period_number for e in batch2_entries]
            lab_periods.sort()
            print(f"   - Batch 2: Lab scheduled on {lab_day}, periods {lab_periods}")
        else:
            print(f"   - Batch 2: ❌ No lab sessions scheduled")
        
        # Check for teacher conflicts
        all_entries = db.query(TimetableEntry).filter(
            TimetableEntry.timetable_id.in_([tt1.timetable_id, tt2.timetable_id])
        ).all()
        
        conflicts = []
        for i, entry1 in enumerate(all_entries):
            for entry2 in all_entries[i+1:]:
                if (entry1.teacher_id == entry2.teacher_id and 
                    entry1.day_of_week == entry2.day_of_week and 
                    entry1.period_number == entry2.period_number and
                    entry1.teacher_id is not None):
                    conflicts.append((entry1, entry2))
        
        if conflicts:
            print(f"\n⚠️ Teacher Conflicts Found: {len(conflicts)}")
            for entry1, entry2 in conflicts:
                print(f"   - Teacher {entry1.teacher_id}: {entry1.day_of_week.value} period {entry1.period_number}")
        else:
            print(f"\n✅ No teacher conflicts found!")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_lab_conflict_resolution()
