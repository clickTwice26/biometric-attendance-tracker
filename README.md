# Fingerprint Attendance System - Backend

Professional Flask-based REST API for biometric attendance management system integrating ESP32 with AS608 fingerprint sensors. Features both web interface and RESTful API for comprehensive attendance tracking.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FINGERPRINT ATTENDANCE SYSTEM                     │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐         WiFi/HTTP          ┌─────────────────┐
    │   ESP32 +    │ ◄────────────────────────► │  Flask Backend  │
    │ AS608 Sensor │    API Communication       │   (Port 8888)   │
    └──────────────┘                            └─────────────────┘
          │                                              │
          │ I²C                                          │
          ▼                                              ▼
    ┌──────────────┐                            ┌─────────────────┐
    │ LCD Display  │                            │ SQLite Database │
    │ (16x2)       │                            │  + Web UI       │
    └──────────────┘                            └─────────────────┘
    
    ┌──────────────┐
    │ Touch Sensor │
    │   + LEDs     │
    └──────────────┘
```

## Key Features

### Backend Features
- 🎓 **Student Management**: CRUD operations with fingerprint enrollment tracking
- 📚 **Class Management**: Class scheduling with day/time slots
- 🔌 **Device Management**: Multi-device support with mode control (idle/attendance/enrollment)
- ✅ **Attendance Tracking**: Real-time attendance with duplicate detection
- 📊 **Web Dashboard**: Modern web interface for all operations
- 🌍 **Timezone Support**: Asia/Dhaka (UTC+6) timezone handling
- 🔄 **Command Queue System**: Asynchronous fingerprint enrollment/deletion
- 📈 **Reports & Analytics**: Attendance statistics and reports

### Hardware Features
- 🔐 **Fingerprint Authentication**: AS608 sensor integration
- 📟 **LCD Feedback**: Real-time status display
- 🚨 **Audio/Visual Indicators**: LEDs and buzzer for user feedback
- 📡 **WiFi Connectivity**: RESTful API communication
- 💾 **Local Storage**: Sensor-based template storage (hybrid mode)

## System Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────────────────────┐
│                          FLASK APPLICATION                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────────┐         ┌─────────────────────┐            │
│  │   Web Frontend     │         │     REST API        │            │
│  │   (Jinja2 HTML)    │         │   (/api/*)          │            │
│  ├────────────────────┤         ├─────────────────────┤            │
│  │ • Dashboard        │         │ • Health            │            │
│  │ • Students CRUD    │         │ • Device Mgmt       │            │
│  │ • Classes CRUD     │         │ • Student API       │            │
│  │ • Devices List     │         │ • Attendance API    │            │
│  │ • Reports          │         │ • Class API         │            │
│  └────────────────────┘         └─────────────────────┘            │
│           │                              │                           │
│           └──────────┬───────────────────┘                           │
│                      ▼                                               │
│  ┌──────────────────────────────────────────────────────┐           │
│  │              BUSINESS LOGIC LAYER                    │           │
│  │   • Fingerprint Template Matching (Hybrid)           │           │
│  │   • Attendance Duplicate Detection                   │           │
│  │   • Command Queue Management                         │           │
│  │   • Timezone Handling (Asia/Dhaka)                   │           │
│  └──────────────────────────────────────────────────────┘           │
│                      ▼                                               │
│  ┌──────────────────────────────────────────────────────┐           │
│  │              DATABASE MODELS (SQLAlchemy)            │           │
│  │   • Student      • Attendance    • Device            │           │
│  │   • Class        • ClassSchedule • Command           │           │
│  └──────────────────────────────────────────────────────┘           │
│                      ▼                                               │
│  ┌──────────────────────────────────────────────────────┐           │
│  │                SQLite Database                       │           │
│  │         instance/fingerprint_attendance.db           │           │
│  └──────────────────────────────────────────────────────┘           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
final-backend/
├── app/
│   ├── __init__.py              # Flask app factory with CORS
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── student.py          # Student model (with fingerprint_template)
│   │   ├── attendance.py       # Attendance records
│   │   ├── device.py           # ESP32 device management
│   │   ├── command.py          # Enrollment/deletion command queue
│   │   ├── class_model.py      # Class/course model
│   │   └── class_schedule.py   # Weekly class schedules
│   ├── routes/                  # Blueprint routes
│   │   ├── __init__.py
│   │   ├── health.py           # Health check endpoint
│   │   ├── device.py           # Device API (mode, poll, commands)
│   │   ├── student.py          # Student CRUD + enrollment
│   │   ├── attendance.py       # Attendance verification & marking
│   │   ├── class_routes.py     # Class CRUD + schedules
│   │   └── frontend.py         # Web UI routes
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── dashboard/          # Dashboard pages
│   │   ├── students/           # Student management UI
│   │   ├── classes/            # Class management UI
│   │   ├── attendance/         # Attendance views
│   │   ├── devices/            # Device listing
│   │   ├── reports/            # Reports & analytics
│   │   └── components/         # Reusable components (navbar)
│   └── utils/
│       ├── __init__.py
│       └── timezone.py         # Dhaka timezone utilities
├── instance/
│   └── fingerprint_attendance.db  # SQLite database
├── config.py                    # Flask configuration
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── script.ino                   # ESP32 Arduino firmware
├── timezone_info.py             # Timezone verification script
├── migrate_schedules.py         # Database migration utility
├── test_backend.sh              # API testing script
├── README.md                    # This file
├── ARDUINO_INTEGRATION.md       # ESP32 integration guide
└── README_SERVERSIDE_MATCHING.md # Template matching docs
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

### REST API Structure
```
http://your-server:8888
│
├── /                          # Web Dashboard (HTML)
├── /students                  # Students Management UI
├── /classes                   # Classes Management UI
├── /devices                   # Devices List UI
├── /attendance               # Attendance Records UI
├── /reports                  # Reports & Analytics UI
│
└── /api/                     # REST API
    ├── /health               # System health check
    ├── /device/              # Device management
    ├── /students/            # Student operations
    ├── /attendance/          # Attendance operations
    └── /classes/             # Class operations
```

### 1. Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Server health status |

**Response:**
```json
{
  "status": "healthy",
  "message": "Fingerprint Attendance System is running",
  "timestamp": "2025-11-16T13:10:40+06:00"
}
```

### 2. Device Management API

| Method | Endpoint | Description | Used By |
|--------|----------|-------------|---------|
| `POST` | `/api/device/mode` | Get device mode and current class | ESP32 (polling) |
| `POST` | `/api/device/poll` | Poll for pending commands | ESP32 (enrollment) |
| `POST` | `/api/device/command/<id>/complete` | Mark command as completed | ESP32 |
| `POST` | `/api/device/set-mode` | Set device mode | Web UI |
| `GET` | `/api/device/list` | List all devices | Web UI |
| `GET` | `/api/device/<device_id>` | Get device details | Web UI |

**Example - Get Device Mode:**
```bash
# Request (ESP32 polls every 5 seconds)
POST /api/device/mode
{
  "device_id": "ESP32-01"
}

# Response
{
  "mode": "attendance",
  "class_id": 1,
  "class_name": "Physics 101",
  "device_id": "ESP32-01"
}
```

**Example - Poll Commands:**
```bash
# Request
POST /api/device/poll
{
  "device_id": "ESP32-01"
}

# Response (when command pending)
{
  "has_command": true,
  "id": 15,
  "command_type": "enroll",
  "fingerprint_id": 5,
  "student_name": "Jane Smith"
}

# Response (no command)
{
  "has_command": false
}
```

### 3. Student Management API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/students/` | List all students (with filters) |
| `GET` | `/api/students/<id>` | Get student by ID |
| `GET` | `/api/students/by-fingerprint/<fp_id>` | Get student by fingerprint ID |
| `POST` | `/api/students/` | Create new student |
| `PUT` | `/api/students/<id>` | Update student |
| `DELETE` | `/api/students/<id>` | Delete student (cascade attendances) |
| `POST` | `/api/students/<id>/enroll` | Queue fingerprint enrollment |
| `POST` | `/api/students/<id>/delete-fingerprint` | Queue fingerprint deletion |

**Example - Create Student:**
```bash
POST /api/students/
{
  "name": "John Doe",
  "email": "john@example.com",
  "student_id": "2024001",
  "fingerprint_id": 1,
  "class_id": 1
}

# Response
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "student_id": "2024001",
  "fingerprint_id": 1,
  "class_id": 1,
  "created_at": "2025-11-16T13:10:40"
}
```

**Example - Enroll Fingerprint:**
```bash
POST /api/students/1/enroll
{
  "device_id": "ESP32-01"
}

# Response
{
  "message": "Enrollment command created",
  "command_id": 15,
  "status": "pending"
}
```

### 4. Attendance API

| Method | Endpoint | Description | Used By |
|--------|----------|-------------|---------|
| `POST` | `/api/attendance/verify` | Verify fingerprint & mark attendance | ESP32 |
| `POST` | `/api/attendance/mark` | Manual attendance marking | Web UI |
| `GET` | `/api/attendance/` | List attendance (filters: date, class, student) | Web UI |
| `GET` | `/api/attendance/<id>` | Get specific attendance record | Web UI |
| `DELETE` | `/api/attendance/<id>` | Delete attendance record | Web UI |
| `GET` | `/api/attendance/stats` | Get attendance statistics | Web UI |

**Example - Verify Fingerprint (ESP32):**
```bash
POST /api/attendance/verify
{
  "fingerprint_id": 1,
  "confidence": 95,
  "device_id": "ESP32-01"
}

# Response - Success
{
  "status": "success",
  "name": "John Doe",
  "message": "Attendance marked for John Doe",
  "class": "Physics 101",
  "timestamp": "2025-11-16T13:10:40+06:00"
}

# Response - Duplicate (within 5 minutes)
{
  "status": "duplicate",
  "name": "John Doe",
  "message": "Attendance already marked recently"
}

# Response - Not Found
{
  "status": "error",
  "message": "Student not found with fingerprint ID 1"
}
```

**Example - Get Attendance Stats:**
```bash
GET /api/attendance/stats?class_id=1&date=2025-11-16

# Response
{
  "total_students": 30,
  "present": 28,
  "absent": 2,
  "late": 0,
  "attendance_rate": 93.33,
  "class": "Physics 101",
  "date": "2025-11-16"
}
```

### 5. Class Management API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/classes/` | List all classes |
| `GET` | `/api/classes/<id>` | Get class details with schedules |
| `POST` | `/api/classes/` | Create new class |
| `PUT` | `/api/classes/<id>` | Update class |
| `DELETE` | `/api/classes/<id>` | Delete class (cascade schedules) |
| `GET` | `/api/classes/<id>/students` | Get students in class |
| `POST` | `/api/classes/<id>/schedules` | Add class schedule |
| `PUT` | `/api/classes/<id>/schedules/<schedule_id>` | Update schedule |
| `DELETE` | `/api/classes/<id>/schedules/<schedule_id>` | Delete schedule |

**Example - Create Class with Schedules:**
```bash
POST /api/classes/
{
  "name": "Physics 101",
  "code": "PHY101",
  "teacher_name": "Dr. Smith",
  "description": "Introduction to Physics",
  "schedules": [
    {
      "day_of_week": "monday",
      "start_time": "10:00",
      "end_time": "11:30"
    },
    {
      "day_of_week": "wednesday",
      "start_time": "10:00",
      "end_time": "11:30"
    }
  ]
}

# Response
{
  "id": 1,
  "name": "Physics 101",
  "code": "PHY101",
  "teacher_name": "Dr. Smith",
  "schedules": [
    {
      "id": 1,
      "day_of_week": "monday",
      "start_time": "10:00",
      "end_time": "11:30"
    },
    {
      "id": 2,
      "day_of_week": "wednesday",
      "start_time": "10:00",
      "end_time": "11:30"
    }
  ],
  "student_count": 0,
  "is_active": true
}
```

## System Workflows

### 1. Student Enrollment Flow
```
┌─────────┐        ┌─────────┐       ┌─────────┐       ┌─────────┐
│  Admin  │        │   Web   │       │  Flask  │       │  ESP32  │
│   UI    │        │  Server │       │   API   │       │ Device  │
└────┬────┘        └────┬────┘       └────┬────┘       └────┬────┘
     │                  │                  │                 │
     │ 1. Create Student│                  │                 │
     │─────────────────►│                  │                 │
     │                  │ POST /students/  │                 │
     │                  │─────────────────►│                 │
     │                  │                  │ Save to DB      │
     │                  │                  │ (fingerprint_id)│
     │                  │◄─────────────────│                 │
     │                  │                  │                 │
     │ 2. Enroll FP     │                  │                 │
     │─────────────────►│ POST /students/  │                 │
     │                  │      {id}/enroll │                 │
     │                  │─────────────────►│                 │
     │                  │                  │ Create Command  │
     │                  │                  │ (status=pending)│
     │                  │◄─────────────────│                 │
     │                  │                  │                 │
     │                  │                  │    POST /poll   │
     │                  │                  │◄────────────────│
     │                  │                  │ Return Command  │
     │                  │                  │────────────────►│
     │                  │                  │                 │
     │                  │                  │                 │ 3. Scan Finger
     │                  │                  │                 │    (3 times)
     │                  │                  │                 │ 4. Store Template
     │                  │                  │                 │    in AS608
     │                  │                  │  POST /command/ │
     │                  │                  │  {id}/complete  │
     │                  │                  │◄────────────────│
     │                  │                  │ Mark completed  │
     │                  │                  │────────────────►│
     └──────────────────┴──────────────────┴─────────────────┘
```

### 2. Attendance Marking Flow
```
┌─────────┐       ┌─────────┐       ┌─────────┐       ┌──────────┐
│  Admin  │       │  Flask  │       │  ESP32  │       │  AS608   │
│   UI    │       │   API   │       │ Device  │       │  Sensor  │
└────┬────┘       └────┬────┘       └────┬────┘       └────┬─────┘
     │                 │                  │                 │
     │ 1. Set Device   │                  │                 │
     │    to Attendance│                  │                 │
     │    Mode (Class) │                  │                 │
     │────────────────►│                  │                 │
     │ POST /device/   │                  │                 │
     │      set-mode   │  Store in DB     │                 │
     │                 │  (mode, class_id)│                 │
     │                 │                  │  POST /mode     │
     │                 │◄─────────────────│  (polling)      │
     │                 │  Return mode     │                 │
     │                 │  & class info    │                 │
     │                 │─────────────────►│                 │
     │                 │                  │                 │
     │                 │                  │ 2. Touch Sensor │
     │                 │                  │◄────────────────┤
     │                 │                  │    Activated    │
     │                 │                  │                 │
     │                 │                  │ 3. Scan Finger  │
     │                 │                  │────────────────►│
     │                 │                  │    Match in     │
     │                 │                  │◄────────────────┤
     │                 │                  │  Sensor (ID)    │
     │                 │                  │                 │
     │                 │  POST /attendance│                 │
     │                 │      /verify     │                 │
     │                 │◄─────────────────│                 │
     │                 │  {fingerprint_id,│                 │
     │                 │   device_id}     │                 │
     │  Check:         │                  │                 │
     │  • Student valid│                  │                 │
     │  • No duplicate │                  │                 │
     │  • In class     │                  │                 │
     │                 │  Return:         │                 │
     │                 │  name, status    │                 │
     │                 │─────────────────►│                 │
     │                 │                  │ 4. Display      │
     │                 │                  │    on LCD       │
     │                 │                  │    (Green LED)  │
     └─────────────────┴──────────────────┴─────────────────┘
```

### 3. Device Mode Management
```
ESP32 Device States:
┌──────────────────────────────────────────────────────────┐
│                                                            │
│    ┌────────┐                                             │
│    │  IDLE  │◄──────────────┐                            │
│    └───┬────┘               │                            │
│        │                    │                            │
│        │ Admin sets mode    │ Admin stops                │
│        ▼                    │                            │
│    ┌────────────┐           │                            │
│    │ ATTENDANCE │───────────┘                            │
│    │    MODE    │                                        │
│    └────────────┘                                        │
│        │ Touch sensor → Scan → Verify → Mark            │
│        │                                                 │
│        │ Admin sets mode                                │
│        ▼                                                 │
│    ┌────────────┐                                        │
│    │ ENROLLMENT │                                        │
│    │    MODE    │                                        │
│    └────────────┘                                        │
│        │ Poll for commands → Execute → Report           │
│        │                                                 │
│        └─────────────► Back to IDLE when done           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Database Schema

### Entity Relationship Diagram
```
┌─────────────────┐         ┌─────────────────┐
│     Student     │         │      Class      │
├─────────────────┤         ├─────────────────┤
│ • id (PK)       │    ┌────│ • id (PK)       │
│ • name          │    │    │ • name          │
│ • email         │    │    │ • code (UK)     │
│ • student_id(UK)│    │    │ • description   │
│ • fingerprint_id│    │    │ • teacher_name  │
│ • fingerprint_  │    │    │ • schedule      │
│   template      │    │    │ • is_active     │
│ • class_id (FK) │────┘    │ • created_at    │
│ • created_at    │         └────┬────────────┘
│ • updated_at    │              │
└────┬────────────┘              │
     │                           │
     │ 1:N                       │ 1:N
     │                           │
     ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│   Attendance    │         │ ClassSchedule   │
├─────────────────┤         ├─────────────────┤
│ • id (PK)       │         │ • id (PK)       │
│ • student_id(FK)│         │ • class_id (FK) │
│ • class_id (FK) │         │ • day_of_week   │
│ • device_id     │         │ • start_time    │
│ • status        │         │ • end_time      │
│ • confidence    │         │ • created_at    │
│ • timestamp     │         └─────────────────┘
│ • notes         │
└─────────────────┘

┌─────────────────┐         ┌─────────────────┐
│     Device      │         │     Command     │
├─────────────────┤         ├─────────────────┤
│ • id (PK)       │         │ • id (PK)       │
│ • device_id(UK) │         │ • device_id     │
│ • name          │         │ • command_type  │
│ • location      │         │ • fingerprint_id│
│ • mode          │         │ • student_name  │
│ • current_class │         │ • status        │
│   _id (FK)      │         │ • created_at    │
│ • is_active     │         │ • completed_at  │
│ • last_seen     │         │ • error_message │
└─────────────────┘         └─────────────────┘
```

### Table Details

#### Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE,
    student_id VARCHAR(50) UNIQUE,
    fingerprint_id INTEGER UNIQUE NOT NULL,
    fingerprint_template BLOB,           -- 512 bytes (future server-side matching)
    class_id INTEGER,                     -- FK to classes.id
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);
```

#### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,         -- FK to students.id
    class_id INTEGER,                     -- FK to classes.id
    device_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'present', -- present/absent/late
    confidence INTEGER,                   -- Matching confidence (0-100)
    timestamp DATETIME NOT NULL,
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);
```

#### Classes Table
```sql
CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE,
    description TEXT,
    teacher_name VARCHAR(100),
    schedule VARCHAR(200),                -- Legacy field
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME
);
```

#### Class Schedules Table
```sql
CREATE TABLE class_schedules (
    id INTEGER PRIMARY KEY,
    class_id INTEGER NOT NULL,            -- FK to classes.id
    day_of_week VARCHAR(10) NOT NULL,     -- monday, tuesday, etc.
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at DATETIME,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    UNIQUE (class_id, day_of_week)
);
```

#### Devices Table
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY,
    device_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    location VARCHAR(200),
    mode VARCHAR(20) DEFAULT 'idle',      -- idle/attendance/enrollment
    current_class_id INTEGER,             -- FK to classes.id
    is_active BOOLEAN DEFAULT 1,
    last_seen DATETIME,
    FOREIGN KEY (current_class_id) REFERENCES classes(id)
);
```

#### Commands Table
```sql
CREATE TABLE commands (
    id INTEGER PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    command_type VARCHAR(20) NOT NULL,    -- enroll/delete
    fingerprint_id INTEGER NOT NULL,
    student_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending', -- pending/completed/failed
    created_at DATETIME,
    completed_at DATETIME,
    error_message TEXT
);
```

## Complete Usage Workflow

### Scenario: Setting Up and Running Attendance for a Class

#### Step 1: Create a Class
```bash
curl -X POST http://localhost:8888/api/classes/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Physics 101",
    "code": "PHY101",
    "teacher_name": "Dr. Smith",
    "schedules": [
      {"day_of_week": "monday", "start_time": "10:00", "end_time": "11:30"},
      {"day_of_week": "wednesday", "start_time": "10:00", "end_time": "11:30"}
    ]
  }'
```

#### Step 2: Add Students
```bash
# Add first student
curl -X POST http://localhost:8888/api/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@university.edu",
    "student_id": "2024001",
    "fingerprint_id": 1,
    "class_id": 1
  }'

# Add second student
curl -X POST http://localhost:8888/api/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@university.edu",
    "student_id": "2024002",
    "fingerprint_id": 2,
    "class_id": 1
  }'
```

#### Step 3: Enroll Fingerprints
```bash
# Enroll John's fingerprint
curl -X POST http://localhost:8888/api/students/1/enroll \
  -H "Content-Type: application/json" \
  -d '{"device_id": "ESP32-01"}'

# ESP32 will automatically:
# 1. Poll for command
# 2. Prompt user to scan finger 3 times
# 3. Store template in AS608 sensor
# 4. Mark command as completed

# Enroll Jane's fingerprint
curl -X POST http://localhost:8888/api/students/2/enroll \
  -H "Content-Type: application/json" \
  -d '{"device_id": "ESP32-01"}'
```

#### Step 4: Start Attendance Session
```bash
# Set device to attendance mode for Physics 101
curl -X POST http://localhost:8888/api/device/set-mode \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32-01",
    "mode": "attendance",
    "class_id": 1
  }'

# ESP32 will:
# 1. Poll and get mode="attendance"
# 2. Display "Touch to Mark" on LCD
# 3. Wait for fingerprint scans
```

#### Step 5: Students Mark Attendance
```
Students touch sensor → Scan finger → 
ESP32 sends fingerprint_id to /api/attendance/verify →
Server marks attendance → Returns student name →
LCD shows "Welcome John Doe" + Green LED
```

#### Step 6: View Attendance Records
```bash
# Get today's attendance for Physics 101
curl "http://localhost:8888/api/attendance/?class_id=1&date=2025-11-16"

# Get attendance statistics
curl "http://localhost:8888/api/attendance/stats?class_id=1&date=2025-11-16"
```

#### Step 7: Stop Attendance Session
```bash
# Set device back to idle mode
curl -X POST http://localhost:8888/api/device/set-mode \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32-01",
    "mode": "idle"
  }'
```

## ESP32 Hardware Integration

### Hardware Components
```
┌────────────────────────────────────────────────────────┐
│                     ESP32 Device                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐    ┌─────────────┐   ┌──────────┐  │
│  │   AS608      │    │  LCD 16x2   │   │  Touch   │  │
│  │ Fingerprint  │    │  (I²C 0x27) │   │  Sensor  │  │
│  │   Sensor     │    └─────────────┘   │ (Pin 4)  │  │
│  │              │                       └──────────┘  │
│  │  TX → Pin 16 │                                     │
│  │  RX → Pin 17 │     ┌──────────┐   ┌──────────┐   │
│  └──────────────┘     │ Green LED│   │  Red LED │   │
│                       │ (Pin 27) │   │ (Pin 25) │   │
│  ┌──────────────┐     └──────────┘   └──────────┘   │
│  │   Buzzer     │                                     │
│  │  (Pin 26)    │     ┌──────────────────────────┐   │
│  └──────────────┘     │   WiFi Module (Built-in) │   │
│                       └──────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

### Pin Configuration
| Component | Pin | Description |
|-----------|-----|-------------|
| AS608 TX | GPIO 16 | Serial RX for fingerprint sensor |
| AS608 RX | GPIO 17 | Serial TX for fingerprint sensor |
| Touch Sensor | GPIO 4 | Touch detection input |
| Green LED | GPIO 27 | Success indicator |
| Red LED | GPIO 25 | Error indicator |
| Buzzer | GPIO 26 | Audio feedback |
| LCD SDA | GPIO 21 | I²C data (default) |
| LCD SCL | GPIO 22 | I²C clock (default) |

### ESP32 Firmware (script.ino)

The ESP32 runs a continuous loop with the following behavior:

```
┌─────────────────────────────────────────────────────┐
│              ESP32 Main Loop (Every 5s)             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Ensure WiFi Connected                          │
│     └─► Reconnect if disconnected                  │
│                                                     │
│  2. Poll Server Mode                               │
│     POST /api/device/mode                          │
│     └─► Get: mode, class_id, class_name           │
│                                                     │
│  3. Update LCD Display                             │
│     └─► Show current mode & class                  │
│                                                     │
│  4. Execute Mode-Specific Logic:                   │
│                                                     │
│     ┌─ IDLE MODE ─────────────────────┐            │
│     │ • Display: "System Ready"       │            │
│     │ • Wait for mode change          │            │
│     └─────────────────────────────────┘            │
│                                                     │
│     ┌─ ATTENDANCE MODE ───────────────┐            │
│     │ • Display: "Touch to Mark"      │            │
│     │ • Monitor touch sensor          │            │
│     │ • On touch:                     │            │
│     │   1. Scan fingerprint (AS608)   │            │
│     │   2. POST /attendance/verify    │            │
│     │   3. Show result on LCD         │            │
│     │   4. LED + Buzzer feedback      │            │
│     └─────────────────────────────────┘            │
│                                                     │
│     ┌─ ENROLLMENT MODE ───────────────┐            │
│     │ • POST /device/poll             │            │
│     │ • If command pending:           │            │
│     │   1. Display student name       │            │
│     │   2. Prompt for 3 scans         │            │
│     │   3. Store in AS608             │            │
│     │   4. POST /command/X/complete   │            │
│     └─────────────────────────────────┘            │
│                                                     │
│  5. Delay 5 seconds                                │
│     └─► Loop restarts                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Key Features of ESP32 Code

1. **Robust WiFi Management**
   - Automatic reconnection
   - Connection validation before HTTP requests
   - Configurable credentials

2. **HTTP Communication**
   - JSON request/response handling
   - Timeout configurations (5-10s)
   - Error handling and retry logic
   - Debug logging for troubleshooting

3. **Fingerprint Operations**
   - Image capture and template creation
   - Local matching (AS608 sensor)
   - Template extraction (512 bytes)
   - Confidence scoring

4. **User Feedback**
   - 16x2 LCD display with scrolling text
   - Green LED for success
   - Red LED for errors
   - Buzzer for audio feedback

5. **Error Recovery**
   - Sensor initialization checks
   - Communication timeout handling
   - Graceful degradation on failures

### Firmware Configuration

Edit `script.ino` to customize:
```cpp
// WiFi Configuration
const char* ssid = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";

// Server Configuration
const char* serverURL = "http://your-server-ip:8888";

// Device Identity
const char* DEVICE_ID = "ESP32-01";

// Hardware Pins (if different from defaults)
#define TCH_PIN 4
#define RXD2 16
#define TXD2 17
#define RED_LED 25
#define GREEN_LED 27
#define BUZZER 26
```

## Configuration

### Backend Configuration (config.py)
```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/fingerprint_attendance.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Timezone (Asia/Dhaka - UTC+6)
    TIMEZONE = 'Asia/Dhaka'
```

**Environment Variables:**
- `SECRET_KEY`: Session encryption key (change in production)
- `FLASK_ENV`: `development` or `production`
- `DATABASE_URL`: Override default SQLite location

## Development

### Local Development Setup
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# 4. Verify timezone configuration
python3 timezone_info.py

# 5. Run development server
python3 app.py
```

### Testing
```bash
# Test all API endpoints
bash test_backend.sh

# Individual endpoint testing
curl http://localhost:8888/api/health
curl http://localhost:8888/api/students/
curl http://localhost:8888/api/classes/
```

### Database Management
```bash
# Create database backup
cp instance/fingerprint_attendance.db instance/backup_$(date +%Y%m%d_%H%M%S).db

# Migrate class schedules (if upgrading from old version)
python3 migrate_schedules.py

# View database contents (requires sqlite3)
sqlite3 instance/fingerprint_attendance.db
> .tables
> SELECT * FROM students;
> .quit
```

### Debug Mode
```bash
# Enable Flask debug mode (auto-reload on code changes)
export FLASK_ENV=development
export FLASK_DEBUG=1
python3 app.py
```

The application logs all requests and responses to the console with timestamps.

## Production Deployment

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv -y

# Clone repository
git clone <repository-url>
cd final-backend
```

### 2. Configure Environment
```bash
# Set production environment variables
export FLASK_ENV=production
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Create production config
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
DATABASE_URL=sqlite:///instance/fingerprint_attendance.db
EOF
```

### 3. Install Production Server
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (4 worker processes)
gunicorn -w 4 -b 0.0.0.0:8888 --timeout 120 app:app

# Or use systemd service
sudo tee /etc/systemd/system/fingerprint-attendance.service > /dev/null <<EOF
[Unit]
Description=Fingerprint Attendance System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/final-backend
Environment="PATH=/path/to/final-backend/venv/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/path/to/final-backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:8888 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable fingerprint-attendance
sudo systemctl start fingerprint-attendance
```

### 4. Reverse Proxy (Nginx)
```nginx
# /etc/nginx/sites-available/fingerprint-attendance
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase timeout for long-polling endpoints
    location /api/device/ {
        proxy_pass http://127.0.0.1:8888;
        proxy_read_timeout 300s;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/fingerprint-attendance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL/HTTPS (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Security Considerations

### Critical Security Measures

1. **Change Default Credentials**
   ```bash
   # Generate strong secret key
   python3 -c 'import secrets; print(secrets.token_hex(32))'
   ```

2. **Database Security**
   - Regular backups
   - Restrict file permissions: `chmod 600 instance/fingerprint_attendance.db`
   - Consider encrypting fingerprint templates at rest

3. **Network Security**
   - Use HTTPS in production (SSL/TLS)
   - Implement firewall rules (only allow necessary ports)
   - ESP32 should communicate over secure network

4. **Authentication & Authorization** (TODO)
   - Implement user authentication for web UI
   - Add API key authentication for ESP32 devices
   - Role-based access control (admin, teacher, student)

5. **Input Validation**
   - All inputs are validated server-side
   - SQL injection protection (SQLAlchemy ORM)
   - XSS protection in templates

6. **Rate Limiting** (Recommended)
   ```bash
   pip install flask-limiter
   ```
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @app.route('/api/attendance/verify')
   @limiter.limit("60 per minute")
   def verify():
       pass
   ```

7. **Logging & Monitoring**
   - Log all attendance events
   - Monitor failed authentication attempts
   - Set up alerts for unusual activity

### Privacy & Compliance

- **Fingerprint Data**: Stored as templates (not actual images)
- **Data Retention**: Implement policy for attendance record retention
- **User Consent**: Ensure students consent to fingerprint enrollment
- **GDPR/Local Laws**: Comply with local biometric data regulations

## Troubleshooting

### Common Issues

**1. ESP32 can't connect to server**
```
- Check WiFi credentials in script.ino
- Verify server IP and port
- Ensure server is accessible on network
- Check firewall rules
```

**2. Database errors**
```bash
# Reset database (WARNING: deletes all data)
rm instance/fingerprint_attendance.db
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

**3. Fingerprint enrollment fails**
```
- Check AS608 sensor connection (TX/RX pins)
- Verify sensor has power (red LED on sensor)
- Clean fingerprint sensor surface
- Ensure finger is dry and clean
```

**4. Attendance marked multiple times**
```
- System has 5-minute duplicate detection
- Check device clock synchronization
- Verify timezone configuration
```

**5. Timezone issues**
```bash
# Verify timezone
python3 timezone_info.py

# Should show: Asia/Dhaka (UTC+6)
```

## Additional Documentation

- **[ARDUINO_INTEGRATION.md](ARDUINO_INTEGRATION.md)**: Detailed ESP32 integration guide
- **[README_SERVERSIDE_MATCHING.md](README_SERVERSIDE_MATCHING.md)**: Server-side template matching implementation

## Technology Stack

- **Backend**: Flask 3.0, SQLAlchemy, Flask-CORS
- **Database**: SQLite (can be migrated to PostgreSQL/MySQL)
- **Hardware**: ESP32, AS608 Fingerprint Sensor, LCD 16x2
- **Frontend**: Jinja2 Templates, Bootstrap (for web UI)
- **Communication**: HTTP/REST, JSON
- **Timezone**: pytz (Asia/Dhaka)

## Future Enhancements

- [ ] Full server-side fingerprint template matching
- [ ] User authentication and role-based access
- [ ] Mobile app for teachers/students
- [ ] Real-time notifications
- [ ] Advanced reporting and analytics
- [ ] Multi-device synchronization
- [ ] QR code backup authentication
- [ ] Face recognition integration
- [ ] Cloud backup and sync

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Repository: [biometric-attendance-tracker](https://github.com/clickTwice26/biometric-attendance-tracker)
- Issues: Create a GitHub issue
- Documentation: See [ARDUINO_INTEGRATION.md](ARDUINO_INTEGRATION.md) and [README_SERVERSIDE_MATCHING.md](README_SERVERSIDE_MATCHING.md)
