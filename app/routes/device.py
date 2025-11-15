"""
Device Management Routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Device, Command, Class

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
    device.last_seen = datetime.utcnow()
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
    """Mark command as completed or failed"""
    data = request.get_json()
    status = data.get('status', 'completed')
    error_message = data.get('error_message')
    
    command = Command.query.get(command_id)
    if not command:
        return jsonify({'error': 'Command not found'}), 404
    
    command.status = status
    command.completed_at = datetime.utcnow()
    if error_message:
        command.error_message = error_message
    
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
