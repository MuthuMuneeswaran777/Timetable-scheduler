#!/usr/bin/env python3
"""
Test database connection and Room model
"""

import sqlite3
import os

def test_database():
    """Test database connection and Room table"""
    db_path = os.path.join(os.path.dirname(__file__), "dev.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if rooms table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rooms'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Rooms table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(rooms)")
            columns = cursor.fetchall()
            print("Room table columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
            
            # Try to query rooms
            cursor.execute("SELECT COUNT(*) FROM rooms")
            count = cursor.fetchone()[0]
            print(f"✅ Found {count} rooms in database")
            
            # Try to insert a test room
            cursor.execute("""
                INSERT INTO rooms (room_name, capacity, room_type, assigned_batch_id) 
                VALUES (?, ?, ?, ?)
            """, ("Test Room", 30, "CLASSROOM", None))
            
            room_id = cursor.lastrowid
            print(f"✅ Inserted test room with ID: {room_id}")
            
            # Clean up
            cursor.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
            conn.commit()
            print("✅ Cleaned up test room")
            
        else:
            print("❌ Rooms table does not exist")
            
        conn.close()
        print("🎉 Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    test_database()
