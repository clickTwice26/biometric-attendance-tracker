"""
Class Model
"""
from datetime import datetime
from app import db
from app.utils.timezone import get_naive_now

class Class(db.Model):
    """Class model - All datetime fields are stored in Asia/Dhaka timezone (timezone-naive)"""
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    teacher_name = db.Column(db.String(100), nullable=True)
    schedule = db.Column(db.String(200), nullable=True)  # e.g., "Mon/Wed 10:00-11:30" (Legacy field)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_naive_now)  # Stored as Asia/Dhaka time (timezone-naive)
    
    # Relationships
    students = db.relationship('Student', backref='class_obj', lazy=True)
    attendances = db.relationship('Attendance', backref='class_obj', lazy=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'teacher_name': self.teacher_name,
            'schedule': self.schedule,  # Legacy field
            'schedules': [s.to_dict() for s in self.schedules] if hasattr(self, 'schedules') else [],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'student_count': len(self.students) if self.students else 0
        }
    
    def __repr__(self):
        return f'<Class {self.name}>'
