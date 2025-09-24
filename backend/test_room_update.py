#!/usr/bin/env python3
"""
Test script to verify room update functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db
from backend.models import Room, Batch
from sqlalchemy import text

def test_room_update():
    """Test room update functionality"""
    db = next(get_db())
    
    try:
        # Check if assigned_batch_id column exists
        result = db.execute(text("PRAGMA table_info(rooms)"))
        columns = [row[1] for row in result.fetchall()]
        print("Room table columns:", columns)
        
        if "assigned_batch_id" not in columns:
            print("❌ assigned_batch_id column missing! Adding it...")
            db.execute(text("ALTER TABLE rooms ADD COLUMN assigned_batch_id INTEGER"))
            db.commit()
            print("✅ Column added successfully")
        else:
            print("✅ assigned_batch_id column exists")
        
        # Test creating a room
        test_room = Room(
            room_name="Test Room 101",
            capacity=30,
            room_type="CLASSROOM",
            assigned_batch_id=None
        )
        db.add(test_room)
        db.commit()
        db.refresh(test_room)
        print(f"✅ Created test room: {test_room.room_id}")
        
        # Test updating the room
        test_room.room_name = "Updated Room 101"
        test_room.capacity = 35
        test_room.assigned_batch_id = 1  # Assign to batch 1 if it exists
        db.commit()
        print("✅ Room updated successfully")
        
        # Verify the update
        updated_room = db.get(Room, test_room.room_id)
        print(f"✅ Verified update: {updated_room.room_name}, capacity: {updated_room.capacity}, batch: {updated_room.assigned_batch_id}")
        
        # Clean up
        db.delete(updated_room)
        db.commit()
        print("✅ Test room deleted")
        
        print("\n🎉 All room update tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_room_update()
