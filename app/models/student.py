"""
Student Model
"""
from datetime import datetime
from app import db
from app.utils.timezone import get_naive_now

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    fingerprint_id = db.Column(db.Integer, unique=True, nullable=False)  # Kept for reference/ordering
    fingerprint_template = db.Column(db.LargeBinary, nullable=True)  # Raw 512-byte template data
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=get_naive_now)
    updated_at = db.Column(db.DateTime, default=get_naive_now, onupdate=get_naive_now)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def has_verified_fingerprint(self):
        """Check if student has a completed fingerprint enrollment"""
        from app.models.command import Command
        completed_enrollment = Command.query.filter_by(
            fingerprint_id=self.fingerprint_id,
            command_type='enroll',
            status='completed'
        ).first()
        return completed_enrollment is not None
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'student_id': self.student_id,
            'fingerprint_id': self.fingerprint_id,
            'class_id': self.class_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Student {self.name} (FP: {self.fingerprint_id})>'
