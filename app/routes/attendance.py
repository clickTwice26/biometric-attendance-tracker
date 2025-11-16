"""Attendance Routes"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import Attendance, Student, Device, Class

def match_fingerprint_template(template_bytes):
    """Match fingerprint template against all stored templates
    
    Returns: (student, confidence) or (None, 0) if no match
    """
    if len(template_bytes) != 512:
        return None, 0
    
    # Get all students with templates
    students = Student.query.filter(Student.fingerprint_template.isnot(None)).all()
    
    best_match = None
    best_score = 0
    
    for student in students:
        if not student.fingerprint_template or len(student.fingerprint_template) != 512:
            continue
        
        # Calculate matching score (simple byte comparison)
        # In production, use proper fingerprint matching algorithm
        matching_bytes = sum(1 for a, b in zip(template_bytes, student.fingerprint_template) if a == b)
        score = (matching_bytes / 512) * 100
        
        if score > best_score:
            best_score = score
            best_match = student
    
    # Require at least 40% match (adjust threshold as needed)
    if best_score >= 40:
        return best_match, int(best_score)
    
    return None, 0

bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@bp.route('/verify', methods=['POST'])
def verify_and_mark_attendance():
    """Verify fingerprint and mark attendance (supports both ID-based and template-based matching)"""
    data = request.get_json()
    fingerprint_id = data.get('fingerprint_id')  # Legacy: for backward compatibility
    template_hex = data.get('template')  # New: hex-encoded template data
    confidence = data.get('confidence')
    device_id = data.get('device_id', 'ESP32-01')
    
    student = None
    match_confidence = confidence if confidence else 0
    
    # Method 1: Server-side template matching (preferred)
    if template_hex:
        try:
            # Convert hex string to bytes
            template_bytes = bytes.fromhex(template_hex)
            
            # Find matching student by comparing templates
            student, match_confidence = match_fingerprint_template(template_bytes)
            
            if not student:
                return jsonify({
                    'status': 'error',
                    'message': 'Fingerprint not recognized',
                    'confidence': 0
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Template processing error: {str(e)}'
            }), 400
    
    # Method 2: Legacy ID-based lookup (for backward compatibility)
    elif fingerprint_id:
        student = Student.query.filter_by(fingerprint_id=fingerprint_id).first()
        if not student:
            return jsonify({
                'status': 'error',
                'message': 'Student not found',
                'fingerprint_id': fingerprint_id
            }), 404
    
    else:
        return jsonify({
            'status': 'error',
            'message': 'Either fingerprint_id or template is required'
        }), 400
    
    # Get device info
    device = Device.query.filter_by(device_id=device_id).first()
    
    # Check if device is in attendance mode with an active class
    class_id = None
    class_name = None
    if device and device.mode == 'attendance' and device.current_class_id:
        class_id = device.current_class_id
        class_obj = Class.query.get(class_id)
        class_name = class_obj.name if class_obj else None
    
    # Check for duplicate attendance in last 5 minutes
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_attendance = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.timestamp >= five_minutes_ago
    ).first()
    
    if recent_attendance:
        return jsonify({
            'status': 'duplicate',
            'message': 'Attendance already marked recently',
            'name': student.name,
            'timestamp': recent_attendance.timestamp.isoformat()
        }), 200
    
    # Create attendance record
    attendance = Attendance(
        student_id=student.id,
        class_id=class_id,
        device_id=device_id,
        status='present',
        confidence=confidence
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    message = f"Attendance marked for {student.name}"
    if class_name:
        message += f" in {class_name}"
    
    return jsonify({
        'status': 'success',
        'message': message,
        'name': student.name,
        'student_id': student.id,
        'class_name': class_name,
        'timestamp': attendance.timestamp.isoformat()
    }), 200

@bp.route('/mark', methods=['POST'])
def mark_attendance():
    """Manual attendance marking (legacy endpoint)"""
    data = request.get_json()
    fingerprint_id = data.get('fingerprint_id')
    status = data.get('status', 'present')
    device_id = data.get('device_id', 'ESP32-01')
    
    if not fingerprint_id:
        return jsonify({'error': 'fingerprint_id is required'}), 400
    
    student = Student.query.filter_by(fingerprint_id=fingerprint_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    device = Device.query.filter_by(device_id=device_id).first()
    class_id = device.current_class_id if device else None
    
    attendance = Attendance(
        student_id=student.id,
        class_id=class_id,
        device_id=device_id,
        status=status
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify({
        'message': 'Attendance marked successfully',
        'attendance': attendance.to_dict()
    }), 201

@bp.route('/', methods=['GET'])
def list_attendance():
    """List attendance records with filters"""
    student_id = request.args.get('student_id', type=int)
    class_id = request.args.get('class_id', type=int)
    date = request.args.get('date')  # Format: YYYY-MM-DD
    limit = request.args.get('limit', type=int, default=100)
    
    query = Attendance.query
    
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    if class_id:
        query = query.filter_by(class_id=class_id)
    
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            next_day = date_obj + timedelta(days=1)
            query = query.filter(
                Attendance.timestamp >= date_obj,
                Attendance.timestamp < next_day
            )
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    attendances = query.order_by(Attendance.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'attendances': [att.to_dict() for att in attendances],
        'count': len(attendances)
    }), 200

@bp.route('/<int:attendance_id>', methods=['GET'])
def get_attendance(attendance_id):
    """Get specific attendance record"""
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({'error': 'Attendance record not found'}), 404
    
    return jsonify(attendance.to_dict()), 200

@bp.route('/<int:attendance_id>', methods=['DELETE'])
def delete_attendance(attendance_id):
    """Delete attendance record"""
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({'error': 'Attendance record not found'}), 404
    
    db.session.delete(attendance)
    db.session.commit()
    
    return jsonify({'message': 'Attendance record deleted successfully'}), 200

@bp.route('/stats', methods=['GET'])
def get_attendance_stats():
    """Get attendance statistics"""
    class_id = request.args.get('class_id', type=int)
    date = request.args.get('date')
    
    query = Attendance.query
    
    if class_id:
        query = query.filter_by(class_id=class_id)
    
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            next_day = date_obj + timedelta(days=1)
            query = query.filter(
                Attendance.timestamp >= date_obj,
                Attendance.timestamp < next_day
            )
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    total = query.count()
    present = query.filter_by(status='present').count()
    absent = query.filter_by(status='absent').count()
    late = query.filter_by(status='late').count()
    
    return jsonify({
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'attendance_rate': round((present / total * 100) if total > 0 else 0, 2)
    }), 200
