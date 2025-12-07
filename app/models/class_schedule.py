"""
Class Schedule Model
"""
from datetime import datetime
from app import db
from app.utils.timezone import get_naive_now

class ClassSchedule(db.Model):
    """Class schedule model - All times are stored in Asia/Dhaka timezone"""
    __tablename__ = 'class_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)  # monday, tuesday, wednesday, etc.
    start_time = db.Column(db.Time, nullable=False)  # Time in Asia/Dhaka timezone
    end_time = db.Column(db.Time, nullable=False)  # Time in Asia/Dhaka timezone
    created_at = db.Column(db.DateTime, default=get_naive_now)  # Stored as Asia/Dhaka time (timezone-naive)
    
    # Relationships
    class_obj = db.relationship('Class', backref=db.backref('schedules', lazy=True, cascade='all, delete-orphan'))
    
    # Ensure only one schedule per day per class
    __table_args__ = (
        db.UniqueConstraint('class_id', 'day_of_week', name='unique_class_day'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ClassSchedule {self.day_of_week} {self.start_time}-{self.end_time}>'
