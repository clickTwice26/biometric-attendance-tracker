"""
Device Model
"""
from datetime import datetime
from app import db
from app.utils.timezone import get_naive_now

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    mode = db.Column(db.String(20), default='idle')  # idle, attendance, enrollment
    current_class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    current_class = db.relationship('Class', foreign_keys=[current_class_id])
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'location': self.location,
            'mode': self.mode,
            'current_class_id': self.current_class_id,
            'current_class_name': self.current_class.name if self.current_class else None,
            'is_active': self.is_active,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Device {self.device_id} - {self.mode}>'
