"""
Database migration script to add class_schedules table
Run this to update the database schema
"""
from app import create_app, db
from app.models.class_schedule import ClassSchedule

def migrate():
    app = create_app()
    with app.app_context():
        # Create the new table
        db.create_all()
        print("✓ class_schedules table created successfully!")
        print("\nYou can now set up detailed schedules for each class.")
        print("Each class can have multiple days with different times.")
        print("Only one schedule per day per class is allowed.")

if __name__ == '__main__':
    migrate()
