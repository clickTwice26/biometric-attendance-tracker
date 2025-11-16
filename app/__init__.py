"""
Flask Application Factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
from datetime import datetime

db = SQLAlchemy()

def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import health, device, student, attendance, class_routes, frontend
    
    # API blueprints
    app.register_blueprint(health.bp)
    app.register_blueprint(device.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(class_routes.bp)
    
    # Frontend blueprint
    app.register_blueprint(frontend.bp)
    
    # Add datetime to template context and timezone filter
    @app.context_processor
    def inject_datetime():
        return {'datetime': datetime}
    
    # Add Dhaka timezone filter for templates
    @app.template_filter('dhaka_time')
    def dhaka_time_filter(dt):
        """Format datetime in Asia/Dhaka timezone"""
        if dt is None:
            return ''
        from app.utils.timezone import DHAKA_TZ
        import pytz
        # If datetime is naive, assume it's already in Dhaka time
        if dt.tzinfo is None:
            return dt.strftime('%b %d, %Y %I:%M %p')
        # Otherwise convert to Dhaka time
        dhaka_dt = dt.astimezone(DHAKA_TZ)
        return dhaka_dt.strftime('%b %d, %Y %I:%M %p')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Initialize default data
        from app.models import Device
        if not Device.query.filter_by(device_id='ESP32-01').first():
            default_device = Device(
                device_id='ESP32-01',
                name='Main Entrance Device',
                location='Building A - Main Entrance'
            )
            db.session.add(default_device)
            db.session.commit()
    
    return app
