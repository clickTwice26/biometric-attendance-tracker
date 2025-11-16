"""
Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, time, timedelta
from app import db
from app.models import Student, Attendance, Device, Command, Class
from app.utils.timezone import get_naive_now, get_today_start

bp = Blueprint('frontend', __name__)

@bp.route('/')
def index():
    """Dashboard home page"""
    # Get statistics
    total_students = Student.query.count()
    total_classes = Class.query.filter_by(is_active=True).count()
    total_devices = Device.query.count()
    
    # Today's attendance
    today_start = get_today_start()
    today_attendance = Attendance.query.filter(Attendance.timestamp >= today_start).count()
    
    # Recent attendance records
    recent_attendance = Attendance.query.order_by(Attendance.timestamp.desc()).limit(10).all()
    
    # Active devices
    devices = Device.query.all()
    
    return render_template('dashboard/index.html',
                         total_students=total_students,
                         total_classes=total_classes,
                         total_devices=total_devices,
                         today_attendance=today_attendance,
                         recent_attendance=recent_attendance,
                         devices=devices)

@bp.route('/students')
def students_list():
    """Students list page"""
    class_filter = request.args.get('class_id', type=int)
    search = request.args.get('search', '')
    
    query = Student.query
    
    if class_filter:
        query = query.filter_by(class_id=class_filter)
    
    if search:
        query = query.filter(Student.name.contains(search))
    
    students = query.order_by(Student.name).all()
    classes = Class.query.filter_by(is_active=True).all()
    devices = Device.query.all()
    
    return render_template('students/list.html', 
                         students=students, 
                         classes=classes,
                         devices=devices,
                         selected_class=class_filter,
                         search=search)

@bp.route('/students/add', methods=['GET', 'POST'])
def student_add():
    """Add new student and optionally create enrollment command"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        student_id = request.form.get('student_id')
        class_id = request.form.get('class_id', type=int)
        enroll_now = request.form.get('enroll_now') == 'on'
        device_id = request.form.get('device_id')
        
        if not name:
            flash('Student name is required', 'error')
            return redirect(url_for('frontend.student_add'))
        
        # Auto-assign next available fingerprint ID
        max_fp_id = db.session.query(db.func.max(Student.fingerprint_id)).scalar()
        fingerprint_id = (max_fp_id or 0) + 1
        
        # Create student record
        student = Student(
            name=name,
            email=email if email else None,
            student_id=student_id if student_id else None,
            fingerprint_id=fingerprint_id,
            class_id=class_id if class_id else None
        )
        
        db.session.add(student)
        db.session.commit()
        
        # Create enrollment command if requested
        if enroll_now and device_id:
            command = Command(
                device_id=device_id,
                command_type='enroll',
                fingerprint_id=fingerprint_id,
                student_name=name,
                status='pending'
            )
            db.session.add(command)
            
            # Set device to enrollment mode
            device = Device.query.filter_by(device_id=device_id).first()
            if device:
                device.mode = 'enrollment'
            
            db.session.commit()
            
            flash(f'Student {name} added! Enrollment command sent to device. Fingerprint ID: {fingerprint_id}', 'success')
        else:
            flash(f'Student {name} added successfully! Fingerprint ID: {fingerprint_id}. Remember to enroll fingerprint.', 'success')
        
        return redirect(url_for('frontend.students_list'))
    
    classes = Class.query.filter_by(is_active=True).all()
    devices = Device.query.all()
    return render_template('students/add.html', classes=classes, devices=devices)

@bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
def student_edit(student_id):
    """Edit student"""
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.email = request.form.get('email') or None
        student.student_id = request.form.get('student_id') or None
        
        new_fp_id = request.form.get('fingerprint_id', type=int)
        if new_fp_id != student.fingerprint_id:
            existing = Student.query.filter_by(fingerprint_id=new_fp_id).first()
            if existing:
                flash(f'Fingerprint ID {new_fp_id} is already assigned to {existing.name}', 'error')
                return redirect(url_for('frontend.student_edit', student_id=student_id))
            student.fingerprint_id = new_fp_id
        
        student.class_id = request.form.get('class_id', type=int) or None
        
        db.session.commit()
        flash(f'Student {student.name} updated successfully!', 'success')
        return redirect(url_for('frontend.students_list'))
    
    classes = Class.query.filter_by(is_active=True).all()
    return render_template('students/edit.html', student=student, classes=classes)

@bp.route('/students/<int:student_id>/delete', methods=['POST'])
def student_delete(student_id):
    """Delete student"""
    student = Student.query.get_or_404(student_id)
    name = student.name
    
    db.session.delete(student)
    db.session.commit()
    
    flash(f'Student {name} deleted successfully!', 'success')
    return redirect(url_for('frontend.students_list'))

@bp.route('/students/<int:student_id>/enroll', methods=['POST'])
def student_enroll(student_id):
    """Create enrollment command for student"""
    student = Student.query.get_or_404(student_id)
    device_id = request.form.get('device_id')
    
    if not device_id:
        flash('Please select a device for enrollment', 'error')
        return redirect(url_for('frontend.students_list'))
    
    # Get device
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        flash(f'Device {device_id} not found', 'error')
        return redirect(url_for('frontend.students_list'))
    
    # Set device to enrollment mode
    device.mode = 'enrollment'
    
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
    
    flash(f'Enrollment command created for {student.name} on device {device.name}. Please scan finger on device.', 'success')
    return redirect(url_for('frontend.students_list'))

@bp.route('/classes')
def classes_list():
    """Classes list page"""
    classes = Class.query.order_by(Class.name).all()
    return render_template('classes/list.html', classes=classes)

@bp.route('/classes/add', methods=['GET', 'POST'])
def class_add():
    """Add new class"""
    from app.models.class_schedule import ClassSchedule
    from datetime import time
    
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        teacher_name = request.form.get('teacher_name')
        
        if not name:
            flash('Class name is required', 'error')
            return redirect(url_for('frontend.class_add'))
        
        if code:
            existing = Class.query.filter_by(code=code).first()
            if existing:
                flash(f'Class code {code} already exists', 'error')
                return redirect(url_for('frontend.class_add'))
        
        class_obj = Class(
            name=name,
            code=code if code else None,
            description=description if description else None,
            teacher_name=teacher_name if teacher_name else None,
            is_active=True
        )
        
        db.session.add(class_obj)
        db.session.flush()  # Get the class ID before adding schedules
        
        # Process schedules
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        schedule_added = False
        for day in days:
            if request.form.get(f'schedule_{day}_enabled') == 'on':
                start_time_str = request.form.get(f'schedule_{day}_start')
                end_time_str = request.form.get(f'schedule_{day}_end')
                
                if start_time_str and end_time_str:
                    try:
                        start_time = time.fromisoformat(start_time_str)
                        end_time = time.fromisoformat(end_time_str)
                        
                        # Validate end time is after start time
                        if end_time > start_time:
                            schedule = ClassSchedule(
                                class_id=class_obj.id,
                                day_of_week=day,
                                start_time=start_time,
                                end_time=end_time
                            )
                            db.session.add(schedule)
                            schedule_added = True
                        else:
                            flash(f'Error: End time must be after start time for {day.capitalize()}', 'error')
                    except ValueError:
                        flash(f'Error: Invalid time format for {day.capitalize()}', 'error')
        
        db.session.commit()
        
        if schedule_added:
            flash(f'Class {name} added successfully with schedule!', 'success')
        else:
            flash(f'Class {name} added successfully! (No schedule set)', 'success')
        return redirect(url_for('frontend.classes_list'))
    
    return render_template('classes/add.html')

@bp.route('/classes/<int:class_id>/edit', methods=['GET', 'POST'])
def class_edit(class_id):
    """Edit class"""
    from app.models.class_schedule import ClassSchedule
    from datetime import time
    
    class_obj = Class.query.get_or_404(class_id)
    
    if request.method == 'POST':
        class_obj.name = request.form.get('name')
        class_obj.code = request.form.get('code') or None
        class_obj.description = request.form.get('description') or None
        class_obj.teacher_name = request.form.get('teacher_name') or None
        class_obj.is_active = request.form.get('is_active') == 'on'
        
        # Delete existing schedules
        ClassSchedule.query.filter_by(class_id=class_obj.id).delete()
        
        # Process new schedules
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            if request.form.get(f'schedule_{day}_enabled') == 'on':
                start_time_str = request.form.get(f'schedule_{day}_start')
                end_time_str = request.form.get(f'schedule_{day}_end')
                
                if start_time_str and end_time_str:
                    try:
                        start_time = time.fromisoformat(start_time_str)
                        end_time = time.fromisoformat(end_time_str)
                        
                        # Validate end time is after start time
                        if end_time > start_time:
                            schedule = ClassSchedule(
                                class_id=class_obj.id,
                                day_of_week=day,
                                start_time=start_time,
                                end_time=end_time
                            )
                            db.session.add(schedule)
                        else:
                            flash(f'Error: End time must be after start time for {day.capitalize()}', 'error')
                    except ValueError:
                        flash(f'Error: Invalid time format for {day.capitalize()}', 'error')
        
        db.session.commit()
        flash(f'Class {class_obj.name} updated successfully!', 'success')
        return redirect(url_for('frontend.classes_list'))
    
    return render_template('classes/edit.html', class_obj=class_obj)

@bp.route('/classes/<int:class_id>/delete', methods=['POST'])
def class_delete(class_id):
    """Delete class"""
    class_obj = Class.query.get_or_404(class_id)
    name = class_obj.name
    
    db.session.delete(class_obj)
    db.session.commit()
    
    flash(f'Class {name} deleted successfully!', 'success')
    return redirect(url_for('frontend.classes_list'))

@bp.route('/attendance')
def attendance_list():
    """Attendance records page"""
    # Filters
    date_filter = request.args.get('date')
    class_filter = request.args.get('class_id', type=int)
    student_filter = request.args.get('student_id', type=int)
    
    query = Attendance.query
    
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d')
            next_day = date_obj + timedelta(days=1)
            query = query.filter(
                Attendance.timestamp >= date_obj,
                Attendance.timestamp < next_day
            )
        except ValueError:
            flash('Invalid date format', 'error')
    
    if class_filter:
        query = query.filter_by(class_id=class_filter)
    
    if student_filter:
        query = query.filter_by(student_id=student_filter)
    
    attendances = query.order_by(Attendance.timestamp.desc()).limit(100).all()
    
    classes = Class.query.filter_by(is_active=True).all()
    students = Student.query.order_by(Student.name).all()
    
    # Statistics for current filter
    total = query.count()
    present = query.filter_by(status='present').count()
    
    return render_template('attendance/list.html',
                         attendances=attendances,
                         classes=classes,
                         students=students,
                         date_filter=date_filter,
                         class_filter=class_filter,
                         student_filter=student_filter,
                         total=total,
                         present=present)

@bp.route('/devices')
def devices_list():
    """Devices management page"""
    devices = Device.query.all()
    classes = Class.query.filter_by(is_active=True).all()
    return render_template('devices/list.html', devices=devices, classes=classes)

@bp.route('/devices/<device_id>/set-mode', methods=['POST'])
def device_set_mode(device_id):
    """Set device mode"""
    device = Device.query.filter_by(device_id=device_id).first_or_404()
    
    mode = request.form.get('mode')
    class_id = request.form.get('class_id', type=int)
    
    if mode not in ['idle', 'attendance', 'enrollment']:
        flash('Invalid mode', 'error')
        return redirect(url_for('frontend.devices_list'))
    
    device.mode = mode
    
    if mode == 'attendance' and class_id:
        device.current_class_id = class_id
    else:
        device.current_class_id = None
    
    db.session.commit()
    
    flash(f'Device {device.name} mode set to {mode}', 'success')
    return redirect(url_for('frontend.devices_list'))

@bp.route('/reports')
def reports():
    """Reports page"""
    # Get date range from query params or default to this month
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    class_filter = request.args.get('class_id', type=int)
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
    else:
        # Default to current month
        today = get_naive_now()
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = today.strftime('%Y-%m-%d')
    
    # Build query
    query = Attendance.query.filter(
        Attendance.timestamp >= start_date,
        Attendance.timestamp < end_date
    )
    
    if class_filter:
        query = query.filter_by(class_id=class_filter)
    
    # Get statistics
    total_records = query.count()
    present_count = query.filter_by(status='present').count()
    absent_count = query.filter_by(status='absent').count()
    late_count = query.filter_by(status='late').count()
    
    # Student-wise attendance
    student_stats = db.session.query(
        Student.id,
        Student.name,
        db.func.count(Attendance.id).label('total_attendance')
    ).join(Attendance).filter(
        Attendance.timestamp >= start_date,
        Attendance.timestamp < end_date
    )
    
    if class_filter:
        student_stats = student_stats.filter(Attendance.class_id == class_filter)
    
    student_stats = student_stats.group_by(Student.id).order_by(
        db.func.count(Attendance.id).desc()
    ).limit(10).all()
    
    classes = Class.query.filter_by(is_active=True).all()
    
    return render_template('reports/index.html',
                         total_records=total_records,
                         present_count=present_count,
                         absent_count=absent_count,
                         late_count=late_count,
                         student_stats=student_stats,
                         classes=classes,
                         start_date=start_date_str,
                         end_date=end_date_str,
                         class_filter=class_filter)
