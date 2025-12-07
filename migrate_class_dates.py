#!/usr/bin/env python3
"""
Migration script to add start_date, end_date, and total_classes fields to classes table
"""
import sqlite3
from datetime import datetime

DB_PATH = 'instance/fingerprint_attendance.db'

def migrate():
    """Add new fields to classes table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== Adding new fields to classes table ===\n")
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(classes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add start_date column if it doesn't exist
        if 'start_date' not in columns:
            print("Adding start_date column...")
            cursor.execute("ALTER TABLE classes ADD COLUMN start_date DATE")
            print("✓ start_date column added")
        else:
            print("✓ start_date column already exists")
        
        # Add end_date column if it doesn't exist
        if 'end_date' not in columns:
            print("Adding end_date column...")
            cursor.execute("ALTER TABLE classes ADD COLUMN end_date DATE")
            print("✓ end_date column added")
        else:
            print("✓ end_date column already exists")
        
        # Add total_classes column if it doesn't exist
        if 'total_classes' not in columns:
            print("Adding total_classes column...")
            cursor.execute("ALTER TABLE classes ADD COLUMN total_classes INTEGER")
            print("✓ total_classes column added")
        else:
            print("✓ total_classes column already exists")
        
        conn.commit()
        print("\n=== Migration completed successfully! ===")
        
        # Show current classes
        cursor.execute("SELECT id, name, start_date, end_date, total_classes FROM classes")
        classes = cursor.fetchall()
        
        if classes:
            print(f"\nCurrent classes ({len(classes)}):")
            for cls in classes:
                print(f"  ID {cls[0]}: {cls[1]}")
                print(f"    Start Date: {cls[2] or 'Not set'}")
                print(f"    End Date: {cls[3] or 'Not set'}")
                print(f"    Total Classes: {cls[4] or 'Not calculated'}")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
