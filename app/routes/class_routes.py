"""
Class Management Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Class, Student

bp = Blueprint('classes', __name__, url_prefix='/api/classes')

@bp.route('/', methods=['GET'])
def list_classes():
    """List all classes"""
    active_only = request.args.get('active', 'false').lower() == 'true'
    
    query = Class.query
    if active_only:
        query = query.filter_by(is_active=True)
    
    classes = query.order_by(Class.name).all()
    return jsonify({
        'classes': [cls.to_dict() for cls in classes]
    }), 200

@bp.route('/<int:class_id>', methods=['GET'])
def get_class(class_id):
    """Get class by ID"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    return jsonify(class_obj.to_dict()), 200

@bp.route('/', methods=['POST'])
def create_class():
    """Create new class"""
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'name is required'}), 400
    
    # Check if code already exists
    if data.get('code'):
        existing = Class.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({'error': 'Class code already exists'}), 409
    
    class_obj = Class(
        name=data['name'],
        code=data.get('code'),
        description=data.get('description'),
        teacher_name=data.get('teacher_name'),
        schedule=data.get('schedule'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(class_obj)
    db.session.commit()
    
    return jsonify({
        'message': 'Class created successfully',
        'class': class_obj.to_dict()
    }), 201

@bp.route('/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    """Update class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        class_obj.name = data['name']
    if 'code' in data:
        # Check if new code is already taken
        existing = Class.query.filter(
            Class.code == data['code'],
            Class.id != class_id
        ).first()
        if existing:
            return jsonify({'error': 'Class code already exists'}), 409
        class_obj.code = data['code']
    if 'description' in data:
        class_obj.description = data['description']
    if 'teacher_name' in data:
        class_obj.teacher_name = data['teacher_name']
    if 'schedule' in data:
        class_obj.schedule = data['schedule']
    if 'is_active' in data:
        class_obj.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Class updated successfully',
        'class': class_obj.to_dict()
    }), 200

@bp.route('/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    """Delete class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    db.session.delete(class_obj)
    db.session.commit()
    
    return jsonify({'message': 'Class deleted successfully'}), 200

@bp.route('/<int:class_id>/students', methods=['GET'])
def get_class_students(class_id):
    """Get all students in a class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    students = Student.query.filter_by(class_id=class_id).order_by(Student.name).all()
    
    return jsonify({
        'class': class_obj.to_dict(),
        'students': [student.to_dict() for student in students]
    }), 200
