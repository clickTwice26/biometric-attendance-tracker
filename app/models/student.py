"""
Student Model
"""
from datetime import datetime
from app import db

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    fingerprint_id = db.Column(db.Integer, unique=True, nullable=False)  # Kept for reference/ordering
    fingerprint_template = db.Column(db.LargeBinary, nullable=True)  # Raw 512-byte template data
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    
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
