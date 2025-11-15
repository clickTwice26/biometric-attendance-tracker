"""
Attendance Model
"""
from datetime import datetime
from app import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    device_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='present')  # present, absent, late
    confidence = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'device_id': self.device_id,
            'status': self.status,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.status} @ {self.timestamp}>'
