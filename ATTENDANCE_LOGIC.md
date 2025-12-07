# Attendance System Logic

## Overview
The attendance system now implements intelligent entry/exit tracking with class validation and cooldown periods.

## How It Works

### 1. Class Validation
- **No Class Running**: If no class is currently scheduled, fingerprint scans are rejected with message "No class is currently running"
- **Class Running**: Attendance can only be marked during scheduled class times (based on class schedules)

### 2. Entry/Exit Logic

#### First Scan (Entry)
- Student scans fingerprint → System records **ENTRY**
- Records: `entry_time`, determines if `status` is "present" or "late" (if >5 min after class start)
- Toast notification shows: "Entered" with green icon

#### 3-Minute Cooldown
- Within 3 minutes of entry: Any fingerprint scan is **IGNORED**
- Returns error: "Please wait X more minute(s)"
- Prevents accidental double scans

#### Second Scan (Exit - After 3 Minutes)
- Student scans fingerprint again (after cooldown) → System records **EXIT**
- Updates existing record with: `exit_time`, calculates `duration_minutes`
- Toast notification shows: "Exited" with blue icon and duration (e.g., "2h 15m")

### 3. Status Determination
- **Present**: Student arrived within 5 minutes of class start time
- **Late**: Student arrived more than 5 minutes after class start time

## Database Schema

### Attendance Table Fields
```
- id: Primary key
- student_id: Foreign key to students
- class_id: Foreign key to classes
- device_id: Device that recorded attendance
- status: 'present' or 'late'
- confidence: Fingerprint match confidence
- timestamp: When record was created (same as entry_time)
- entry_time: When student entered class
- exit_time: When student exited class (NULL if still in class)
- duration_minutes: Total time spent in class
- notes: Additional information
```

## API Response Examples

### Entry Response
```json
{
  "status": "entry",
  "message": "John Doe entered Computer Science 101",
  "student_name": "John Doe",
  "student_id": "CS2024001",
  "class_name": "Computer Science 101",
  "entry_time": "10:05:23",
  "attendance_status": "late",
  "confidence": 95,
  "attendance_id": 123
}
```

### Cooldown Response (Within 3 Minutes)
```json
{
  "status": "cooldown",
  "message": "Please wait 2 more minute(s)",
  "details": "You must wait 3 minutes between entry and exit",
  "student_name": "John Doe",
  "last_scan": "2025-12-07T10:05:23"
}
```

### Exit Response
```json
{
  "status": "exit",
  "message": "John Doe exited from Computer Science 101",
  "student_name": "John Doe",
  "class_name": "Computer Science 101",
  "entry_time": "10:05:23",
  "exit_time": "11:50:15",
  "duration_minutes": 105,
  "attendance_id": 123
}
```

### No Class Running Response
```json
{
  "status": "error",
  "message": "No class is currently running",
  "details": "Attendance can only be marked during scheduled class times",
  "student_name": "John Doe"
}
```

## Dashboard Real-Time Features

### Current Running Class Card
- Shows currently active class with gradient background (indigo/purple)
- Turns gray when no class is running
- Updates every 30 seconds

### Toast Notifications
- **Entry**: Green border, "sign-in" icon, shows student entered
- **Exit**: Blue border, "sign-out" icon, shows duration spent
- **Late Entry**: Yellow border, "exclamation" icon
- Auto-dismisses after 5-7 seconds
- Different sound tones for entry (900Hz) vs exit (600Hz)

## Migration

Run the migration script to add new fields:
```bash
python migrate_attendance_fields.py
```

This adds:
- `entry_time` column
- `exit_time` column  
- `duration_minutes` column

Existing records are automatically updated with `entry_time = timestamp`.

## Benefits

1. **Accurate Tracking**: Know exactly when students enter and exit
2. **Prevent Abuse**: 3-minute cooldown prevents gaming the system
3. **Class Context**: Attendance only during valid class times
4. **Duration Tracking**: See how long students stay in class
5. **Real-Time Visibility**: Dashboard shows live attendance activity
6. **Better Reports**: Can analyze attendance patterns and class duration
