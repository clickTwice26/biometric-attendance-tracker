"""
Migration script to add entry_time, exit_time, and duration_minutes to attendance table
Run this once to update your database schema
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Add new columns to attendance table
        with db.engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("PRAGMA table_info(attendance)"))
            columns = [row[1] for row in result]
            
            if 'entry_time' not in columns:
                print("Adding entry_time column...")
                conn.execute(text("ALTER TABLE attendance ADD COLUMN entry_time DATETIME"))
                conn.commit()
                print("✓ entry_time column added")
            else:
                print("✓ entry_time column already exists")
            
            if 'exit_time' not in columns:
                print("Adding exit_time column...")
                conn.execute(text("ALTER TABLE attendance ADD COLUMN exit_time DATETIME"))
                conn.commit()
                print("✓ exit_time column added")
            else:
                print("✓ exit_time column already exists")
            
            if 'duration_minutes' not in columns:
                print("Adding duration_minutes column...")
                conn.execute(text("ALTER TABLE attendance ADD COLUMN duration_minutes INTEGER"))
                conn.commit()
                print("✓ duration_minutes column added")
            else:
                print("✓ duration_minutes column already exists")
        
        # Update existing records to set entry_time = timestamp where entry_time is NULL
        with db.engine.connect() as conn:
            print("\nUpdating existing attendance records...")
            conn.execute(text("UPDATE attendance SET entry_time = timestamp WHERE entry_time IS NULL"))
            conn.commit()
            print("✓ Existing records updated")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise

