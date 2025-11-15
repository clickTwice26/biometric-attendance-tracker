"""
Student Management Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Student, Command

bp = Blueprint('students', __name__, url_prefix='/api/students')

@bp.route('/', methods=['GET'])
def list_students():
    """List all students"""
    class_id = request.args.get('class_id', type=int)
    
    query = Student.query
    if class_id:
        query = query.filter_by(class_id=class_id)
    
    students = query.order_by(Student.name).all()
    return jsonify({
        'students': [student.to_dict() for student in students]
    }), 200

@bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get student by ID"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify(student.to_dict()), 200

@bp.route('/by-fingerprint/<int:fingerprint_id>', methods=['GET'])
def get_student_by_fingerprint(fingerprint_id):
    """Get student by fingerprint ID"""
    student = Student.query.filter_by(fingerprint_id=fingerprint_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify(student.to_dict()), 200

@bp.route('/', methods=['POST'])
def create_student():
    """Create new student"""
    data = request.get_json()
    
    required_fields = ['name', 'fingerprint_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'name and fingerprint_id are required'}), 400
    
    # Check if fingerprint_id already exists
    existing = Student.query.filter_by(fingerprint_id=data['fingerprint_id']).first()
    if existing:
        return jsonify({'error': 'Fingerprint ID already exists'}), 409
    
    student = Student(
        name=data['name'],
        email=data.get('email'),
        student_id=data.get('student_id'),
        fingerprint_id=data['fingerprint_id'],
        class_id=data.get('class_id')
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify({
        'message': 'Student created successfully',
        'student': student.to_dict()
    }), 201

@bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update student"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        student.name = data['name']
    if 'email' in data:
        student.email = data['email']
    if 'student_id' in data:
        student.student_id = data['student_id']
    if 'class_id' in data:
        student.class_id = data['class_id']
    if 'fingerprint_id' in data:
        # Check if new fingerprint_id is already taken
        existing = Student.query.filter(
            Student.fingerprint_id == data['fingerprint_id'],
            Student.id != student_id
        ).first()
        if existing:
            return jsonify({'error': 'Fingerprint ID already exists'}), 409
        student.fingerprint_id = data['fingerprint_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Student updated successfully',
        'student': student.to_dict()
    }), 200

@bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete student"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    db.session.delete(student)
    db.session.commit()
    
    return jsonify({'message': 'Student deleted successfully'}), 200

@bp.route('/<int:student_id>/enroll', methods=['POST'])
def enroll_student_fingerprint(student_id):
    """Create enrollment command for device"""
    data = request.get_json()
    device_id = data.get('device_id', 'ESP32-01')
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Create enrollment command
    command = Command(
        device_id=device_id,
        command_type='enroll',
        fingerprint_id=student.fingerprint_id,
        student_name=student.name,
        status='pending'
    )
    
    db.session.add(command)
    db.session.commit()
    
    return jsonify({
        'message': 'Enrollment command created',
        'command': command.to_dict()
    }), 201

@bp.route('/<int:student_id>/delete-fingerprint', methods=['POST'])
def delete_student_fingerprint(student_id):
    """Create delete fingerprint command for device"""
    data = request.get_json()
    device_id = data.get('device_id', 'ESP32-01')
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Create delete command
    command = Command(
        device_id=device_id,
        command_type='delete',
        fingerprint_id=student.fingerprint_id,
        student_name=student.name,
        status='pending'
    )
    
    db.session.add(command)
    db.session.commit()
    
    return jsonify({
        'message': 'Delete fingerprint command created',
        'command': command.to_dict()
    }), 201
