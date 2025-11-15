"""
Command Model for Device Commands
"""
from datetime import datetime
from app import db

class Command(db.Model):
    __tablename__ = 'commands'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    command_type = db.Column(db.String(20), nullable=False)  # enroll, delete
    fingerprint_id = db.Column(db.Integer, nullable=False)
    student_name = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'command_type': self.command_type,
            'fingerprint_id': self.fingerprint_id,
            'student_name': self.student_name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f'<Command {self.command_type} FP:{self.fingerprint_id} - {self.status}>'
