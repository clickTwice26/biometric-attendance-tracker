"""
Attendance Routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import Attendance, Student, Device, Class
from app.utils.timezone import get_naive_now

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
    """Verify fingerprint and mark attendance with entry/exit tracking and class validation"""
    import logging
    
    data = request.get_json()
    fingerprint_id = data.get('fingerprint_id')  # Legacy: for backward compatibility
    template_hex = data.get('template')  # New: hex-encoded template data
    confidence = data.get('confidence')
    device_id = data.get('device_id', 'ESP32-01')
    
    logging.info(f"=== ATTENDANCE VERIFY REQUEST ===")
    logging.info(f"Device ID: {device_id}")
    logging.info(f"Fingerprint ID: {fingerprint_id}")
    logging.info(f"Confidence: {confidence}")
    logging.info(f"Template provided: {bool(template_hex)}")
    
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
        logging.info(f"Looking up student by fingerprint_id: {fingerprint_id}")
        student = Student.query.filter_by(fingerprint_id=fingerprint_id).first()
        if not student:
            logging.warning(f"Student not found for fingerprint_id: {fingerprint_id}")
            return jsonify({
                'status': 'error',
                'message': 'Student not found',
                'fingerprint_id': fingerprint_id
            }), 404
        logging.info(f"Found student: {student.name} (ID: {student.id})")
    
    else:
        logging.error("Neither fingerprint_id nor template provided")
        return jsonify({
            'status': 'error',
            'message': 'Either fingerprint_id or template is required'
        }), 400
    
    # STEP 0: Check if device is in enrollment mode - reject attendance scans during enrollment
    device = Device.query.filter_by(device_id=device_id).first()
    logging.info(f"Device lookup: {device_id}, Found: {device is not None}, Mode: {device.mode if device else 'N/A'}")
    
    if device and device.mode == 'enrollment':
        logging.warning(f"Rejecting attendance for {student.name} - Device in enrollment mode")
        return jsonify({
            'status': 'error',
            'message': 'Enrollment mode',
            'details': 'Device is in enrollment mode. Attendance not recorded.',
            'student_name': student.name
        }), 400
    
    # STEP 1: Check if there is a currently running class
    from app.routes.frontend import get_current_running_class
    
    current_class = get_current_running_class()
    logging.info(f"Current running class: {current_class}")
    
    if not current_class:
        logging.warning(f"Attendance attempt by {student.name} ({student.student_id}) - No class running")
        return jsonify({
            'status': 'error',
            'message': 'No class running',
            'details': 'Attendance can only be marked during scheduled class times',
            'student_name': student.name
        }), 400
    
    class_id = current_class['id']
    class_name = current_class['name']
    logging.info(f"Class ID: {class_id}, Class Name: {class_name}")
    
    # STEP 2: Check for recent attendance (within 3 minutes)
    now = get_naive_now()
    three_minutes_ago = now - timedelta(minutes=3)
    logging.info(f"Current time: {now}, Checking attendance since: {three_minutes_ago}")
    
    recent_attendance = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.class_id == class_id,
        Attendance.timestamp >= three_minutes_ago
    ).order_by(Attendance.timestamp.desc()).first()
    
    logging.info(f"Recent attendance found: {recent_attendance is not None}")
    
    # STEP 3: Handle entry/exit logic
    if recent_attendance:
        # Within 3 minutes - ignore the fingerprint scan
        time_diff = (now - recent_attendance.timestamp).total_seconds() / 60
        logging.warning(f"Cooldown active for {student.name} - Last scan {time_diff:.1f} minutes ago")
        return jsonify({
            'status': 'cooldown',
            'message': f'Please wait {int(3 - time_diff)} more minute(s)',
            'details': 'You must wait 3 minutes between entry and exit',
            'student_name': student.name,
            'last_scan': recent_attendance.timestamp.isoformat()
        }), 400
    
    # Check if there's an existing attendance record for this class today without exit
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    logging.info(f"Checking for completed attendance since: {today_start}")
    
    # First check if student already has BOTH entry and exit for this class today
    completed_attendance = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.class_id == class_id,
        Attendance.timestamp >= today_start,
        Attendance.entry_time.isnot(None),
        Attendance.exit_time.isnot(None)
    ).first()
    
    if completed_attendance:
        # Student already completed entry and exit for this class
        logging.warning(f"{student.name} already has completed attendance for {class_name}")
        return jsonify({
            'status': 'error',
            'message': 'Already recorded',
            'details': f'Entry and exit already marked for {class_name}',
            'student_name': student.name,
            'class_name': class_name,
            'entry_time': completed_attendance.entry_time.strftime('%H:%M:%S'),
            'exit_time': completed_attendance.exit_time.strftime('%H:%M:%S'),
            'duration_minutes': completed_attendance.duration_minutes
        }), 400
    
    # Now check for pending entry (no exit yet)
    existing_entry = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.class_id == class_id,
        Attendance.timestamp >= today_start,
        Attendance.exit_time.is_(None)
    ).first()
    
    logging.info(f"Existing entry without exit found: {existing_entry is not None}")
    
    if existing_entry:
        # This is an EXIT scan (after 3 minutes cooldown has passed)
        logging.info(f"Processing EXIT for {student.name}")
        existing_entry.exit_time = now
        
        # Calculate duration in minutes
        if existing_entry.entry_time:
            duration = (now - existing_entry.entry_time).total_seconds() / 60
            existing_entry.duration_minutes = int(duration)
        
        existing_entry.notes = f"Exited at {now.strftime('%H:%M:%S')}"
        
        db.session.commit()
        
        logging.info(f"EXIT recorded - Duration: {existing_entry.duration_minutes} minutes")
        
        return jsonify({
            'status': 'exit',
            'message': f'{student.name} exited from {class_name}',
            'student_name': student.name,
            'class_name': class_name,
            'entry_time': existing_entry.entry_time.strftime('%H:%M:%S'),
            'exit_time': now.strftime('%H:%M:%S'),
            'duration_minutes': existing_entry.duration_minutes,
            'attendance_status': existing_entry.status,
            'attendance_id': existing_entry.id
        }), 200
    
    # This is an ENTRY scan (first scan or new session)
    logging.info(f"Processing ENTRY for {student.name}")
    # Determine if student is late
    class_start_time = datetime.strptime(current_class['start_time'], '%H:%M').time()
    class_end_time = datetime.strptime(current_class['end_time'], '%H:%M').time()
    current_time = now.time()
    
    # Calculate time remaining until class ends
    class_end_datetime = datetime.combine(datetime.today(), class_end_time)
    current_datetime = datetime.combine(datetime.today(), current_time)
    time_remaining_minutes = int((class_end_datetime - current_datetime).total_seconds() / 60)
    
    status = 'present'
    late_by_minutes = 0
    if current_time > class_start_time:
        # Late if more than 5 minutes after class start
        time_diff_minutes = (datetime.combine(datetime.today(), current_time) - 
                            datetime.combine(datetime.today(), class_start_time)).total_seconds() / 60
        if time_diff_minutes > 5:
            status = 'late'
            late_by_minutes = int(time_diff_minutes)
            logging.info(f"Student is LATE by {late_by_minutes} minutes")
        else:
            logging.info(f"Student is ON TIME (within 5 min grace period)")
    else:
        logging.info(f"Student is EARLY")
    
    # Create new attendance record for ENTRY
    attendance = Attendance(
        student_id=student.id,
        class_id=class_id,
        device_id=device_id,
        status=status,
        confidence=match_confidence,
        timestamp=now,
        entry_time=now,
        notes=f"Entered at {now.strftime('%H:%M:%S')}" + (f" (Late by {late_by_minutes} min)" if status == 'late' else "")
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    logging.info(f"ENTRY recorded successfully - Attendance ID: {attendance.id}")
    
    return jsonify({
        'status': 'entry',
        'message': f'{student.name} entered {class_name}',
        'student_name': student.name,
        'student_id': student.student_id,
        'class_name': class_name,
        'entry_time': now.strftime('%H:%M:%S'),
        'class_end_time': current_class['end_time'],
        'time_remaining_minutes': time_remaining_minutes,
        'attendance_status': status,
        'late_by_minutes': late_by_minutes if status == 'late' else 0,
        'confidence': match_confidence,
        'attendance_id': attendance.id
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
