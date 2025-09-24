#!/usr/bin/env python3
"""
Migration script to add assigned_batch_id column to rooms table
"""

import sqlite3
import os

def migrate_database():
    """Add assigned_batch_id column to rooms table if it doesn't exist"""
    db_path = os.path.join(os.path.dirname(__file__), "dev.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(rooms)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "assigned_batch_id" not in columns:
            print("Adding assigned_batch_id column to rooms table...")
            cursor.execute("ALTER TABLE rooms ADD COLUMN assigned_batch_id INTEGER")
            conn.commit()
            print("✅ Column added successfully!")
        else:
            print("✅ assigned_batch_id column already exists")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(rooms)")
        columns = [row[1] for row in cursor.fetchall()]
        print("Current room table columns:", columns)
        
        conn.close()
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_database()
