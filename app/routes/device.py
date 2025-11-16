"""
Device Management Routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import Device, Command, Class
from app.utils.timezone import get_naive_now

bp = Blueprint('device', __name__, url_prefix='/api/device')

@bp.route('/mode', methods=['POST'])
def get_device_mode():
    """Get current device mode and class info"""
    data = request.get_json()
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    # Update last seen
    device.last_seen = get_naive_now()
    db.session.commit()
    
    response = {
        'mode': device.mode,
        'device_id': device.device_id,
        'device_name': device.name
    }
    
    # Include class info if in attendance mode
    if device.mode == 'attendance' and device.current_class:
        response['class_id'] = device.current_class_id
        response['class_name'] = device.current_class.name
    
    return jsonify(response), 200

@bp.route('/poll', methods=['POST'])
def poll_commands():
    """Poll for pending commands"""
    data = request.get_json()
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    # Get pending command for this device
    command = Command.query.filter_by(
        device_id=device_id,
        status='pending'
    ).order_by(Command.created_at.asc()).first()
    
    if not command:
        return jsonify({
            'has_command': False,
            'message': 'No pending commands'
        }), 200
    x = {
        'has_command': True,
        'id': command.id,
        'command_type': command.command_type,
        'fingerprint_id': command.fingerprint_id,
        'student_name': command.student_name or 'Unknown'
    }
    print(x)
    return jsonify(x), 200

@bp.route('/command/<int:command_id>/complete', methods=['POST'])
def complete_command(command_id):
    """Mark command as completed or failed (supports template upload for enrollment)"""
    try:
        data = request.get_json()
        if not data:
            print(f"ERROR: No JSON data received for command {command_id}")
            return jsonify({'error': 'No JSON data received'}), 400
        
        print(f"Command {command_id} completion request: {data}")
        
        status = data.get('status', 'completed')
        error_message = data.get('error_message')
        template_hex = data.get('template')  # Hex-encoded template data from enrollment
        
        command = Command.query.get(command_id)
        if not command:
            print(f"ERROR: Command {command_id} not found")
            return jsonify({'error': 'Command not found'}), 404
    except Exception as e:
        print(f"ERROR parsing request for command {command_id}: {str(e)}")
        return jsonify({'error': f'Request parsing failed: {str(e)}'}), 400
    
    # If enrollment completed successfully and template provided, store it
    # Note: Hybrid approach - templates stored in sensor, metadata in server
    if status == 'completed' and command.command_type == 'enroll' and template_hex and len(template_hex) > 0:
        try:
            from app.models import Student
            
            # Convert hex string to bytes
            template_bytes = bytes.fromhex(template_hex)
            
            if len(template_bytes) != 512:
                print(template_bytes)
                return jsonify({'error': 'Invalid template size (must be 512 bytes)'}), 400
            
            # Find student by fingerprint_id and store template
            student = Student.query.filter_by(fingerprint_id=command.fingerprint_id).first()
            if student:
                student.fingerprint_template = template_bytes
                db.session.commit()
                print(f"Stored template for student: {student.name} (ID: {student.id})")
            else:
                print(f"Warning: Student not found for fingerprint_id: {command.fingerprint_id}")
                
        except Exception as e:
            print(f"Error storing template: {str(e)}")
            return jsonify({'error': f'Template storage failed: {str(e)}'}), 400
    elif status == 'completed' and command.command_type == 'enroll':
        # Hybrid approach: template stored in sensor, not uploaded to server
        print(f"Enrollment completed (hybrid mode - template stored in sensor only)")
    
    command.status = status
    command.completed_at = get_naive_now()
    if error_message:
        command.error_message = error_message
    
    # Auto-reset device mode to idle after command completion
    if status == 'completed' and command.command_type == 'enroll':
        device = Device.query.filter_by(device_id=command.device_id).first()
        if device and device.mode == 'enrollment':
            device.mode = 'idle'
            print(f"Device {device.device_id} mode reset to idle after enrollment")
    
    db.session.commit()
    
    return jsonify({
        'message': f'Command {status}',
        'command': command.to_dict()
    }), 200

@bp.route('/set-mode', methods=['POST'])
def set_device_mode():
    """Set device mode (admin endpoint)"""
    data = request.get_json()
    device_id = data.get('device_id')
    mode = data.get('mode')
    class_id = data.get('class_id')
    
    if not device_id or not mode:
        return jsonify({'error': 'device_id and mode are required'}), 400
    
    if mode not in ['idle', 'attendance', 'enrollment']:
        return jsonify({'error': 'Invalid mode'}), 400
    
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    device.mode = mode
    
    if mode == 'attendance' and class_id:
        device.current_class_id = class_id
    elif mode != 'attendance':
        device.current_class_id = None
    
    db.session.commit()
    
    return jsonify({
        'message': f'Device mode set to {mode}',
        'device': device.to_dict()
    }), 200

@bp.route('/list', methods=['GET'])
def list_devices():
    """List all devices"""
    devices = Device.query.all()
    return jsonify({
        'devices': [device.to_dict() for device in devices]
    }), 200

@bp.route('/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get device details"""
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    return jsonify(device.to_dict()), 200
