# Fingerprint Attendance System - Backend

Professional Flask-based REST API for fingerprint attendance management with SQLite database.

## Features

- **Student Management**: CRUD operations for students with fingerprint mapping
- **Class Management**: Create and manage classes/courses
- **Device Management**: Control ESP32 devices, set modes, and handle commands
- **Attendance Tracking**: Real-time attendance marking with fingerprint verification
- **Command System**: Queue enrollment/deletion commands for devices
- **Statistics & Reporting**: Attendance analytics and reports

## Project Structure

```
final-backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── attendance.py
│   │   ├── device.py
│   │   ├── command.py
│   │   └── class_model.py
│   └── routes/              # API endpoints
│       ├── __init__.py
│       ├── health.py        # Health check
│       ├── device.py        # Device management
│       ├── student.py       # Student CRUD
│       ├── attendance.py    # Attendance marking
│       └── class_routes.py  # Class management
├── config.py                # Configuration
├── app.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── script.ino              # ESP32 Arduino code
└── README.md               # This file
```

## Installation

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize database:**
```bash
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

4. **Run the server:**
```bash
python3 app.py
```

The server will start on `http://0.0.0.0:8888`

## API Endpoints

### Health Check
- `GET /api/health` - Check if server is running

### Device Management
- `POST /api/device/mode` - Get device mode and current class
- `POST /api/device/poll` - Poll for pending commands
- `POST /api/device/command/<id>/complete` - Mark command as completed
- `POST /api/device/set-mode` - Set device mode (idle/attendance/enrollment)
- `GET /api/device/list` - List all devices
- `GET /api/device/<device_id>` - Get device details

### Student Management
- `GET /api/students/` - List all students
- `GET /api/students/<id>` - Get student by ID
- `GET /api/students/by-fingerprint/<fp_id>` - Get student by fingerprint ID
- `POST /api/students/` - Create new student
- `PUT /api/students/<id>` - Update student
- `DELETE /api/students/<id>` - Delete student
- `POST /api/students/<id>/enroll` - Create enrollment command
- `POST /api/students/<id>/delete-fingerprint` - Create delete fingerprint command

### Attendance
- `POST /api/attendance/verify` - Verify fingerprint and mark attendance
- `POST /api/attendance/mark` - Manual attendance marking
- `GET /api/attendance/` - List attendance records (with filters)
- `GET /api/attendance/<id>` - Get specific attendance record
- `DELETE /api/attendance/<id>` - Delete attendance record
- `GET /api/attendance/stats` - Get attendance statistics

### Class Management
- `GET /api/classes/` - List all classes
- `GET /api/classes/<id>` - Get class by ID
- `POST /api/classes/` - Create new class
- `PUT /api/classes/<id>` - Update class
- `DELETE /api/classes/<id>` - Delete class
- `GET /api/classes/<id>/students` - Get students in class

## Database Schema

### Students Table
- `id` (Primary Key)
- `name` (String, Required)
- `email` (String, Unique)
- `student_id` (String, Unique)
- `fingerprint_id` (Integer, Unique, Required)
- `class_id` (Foreign Key to Classes)
- `created_at`, `updated_at`

### Attendance Table
- `id` (Primary Key)
- `student_id` (Foreign Key)
- `class_id` (Foreign Key)
- `device_id` (String)
- `status` (present/absent/late)
- `confidence` (Integer)
- `timestamp`
- `notes`

### Devices Table
- `id` (Primary Key)
- `device_id` (String, Unique)
- `name`, `location`
- `mode` (idle/attendance/enrollment)
- `current_class_id` (Foreign Key)
- `is_active`, `last_seen`

### Commands Table
- `id` (Primary Key)
- `device_id`, `command_type`
- `fingerprint_id`, `student_name`
- `status` (pending/completed/failed)
- `created_at`, `completed_at`

### Classes Table
- `id` (Primary Key)
- `name`, `code` (Unique)
- `description`, `teacher_name`
- `schedule`, `is_active`

## Usage Examples

### 1. Create a Class
```bash
curl -X POST http://localhost:8888/api/classes/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Computer Science 101",
    "code": "CS101",
    "teacher_name": "Dr. Smith",
    "schedule": "Mon/Wed 10:00-11:30"
  }'
```

### 2. Add a Student
```bash
curl -X POST http://localhost:8888/api/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "student_id": "2024001",
    "fingerprint_id": 1,
    "class_id": 1
  }'
```

### 3. Enroll Fingerprint
```bash
curl -X POST http://localhost:8888/api/students/1/enroll \
  -H "Content-Type: application/json" \
  -d '{"device_id": "ESP32-01"}'
```

### 4. Set Device to Attendance Mode
```bash
curl -X POST http://localhost:8888/api/device/set-mode \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32-01",
    "mode": "attendance",
    "class_id": 1
  }'
```

### 5. Check Attendance Stats
```bash
curl http://localhost:8888/api/attendance/stats?class_id=1&date=2024-11-15
```

## Configuration

Edit `config.py` to customize:
- Database location
- Secret key
- Session lifetime
- Debug mode

## ESP32 Integration

The ESP32 device (script.ino):
1. Polls `/api/device/mode` every 5 seconds for mode updates
2. Polls `/api/device/poll` for pending commands when in enrollment mode
3. Sends fingerprint scans to `/api/attendance/verify`
4. Reports command completion to `/api/device/command/<id>/complete`

## Development

**Enable debug mode:**
```bash
export FLASK_ENV=development
python3 app.py
```

**View logs:**
The application logs all requests and responses to the console.

## Production Deployment

1. Set environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-random-key
```

2. Use a production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8888 app:app
```

## Security Notes

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Implement authentication/authorization
- Rate limit API endpoints
- Validate all user inputs

## License

MIT License - See LICENSE file for details
