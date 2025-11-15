# Arduino ESP32 Integration Guide

## Updates Made to script.ino

The Arduino script has been updated to work smoothly with the Flask backend. Here are the key improvements:

### 1. **Enhanced Error Handling**
- Added comprehensive bounds checking for all JSON parsing operations
- Better WiFi connection validation with `ensureWiFiConnection()`
- Improved HTTP error handling with detailed logging
- Added timeout configurations for all HTTP requests (5-10 seconds)

### 2. **Backend API Integration**
The script now properly integrates with these Flask endpoints:

#### `/api/attendance/verify` (POST)
- **Purpose**: Verify fingerprint and mark attendance
- **Payload**: `{"fingerprint_id": 1, "confidence": 95, "device_id": "ESP32-01"}`
- **Responses**:
  - `200 OK` with `{"status": "success", "name": "John Doe", "message": "..."}`
  - `200 OK` with `{"status": "duplicate", "name": "John Doe", "message": "Already marked"}`
  - `404 Not Found` with `{"status": "error", "message": "Student not found"}`
  - `200 OK` with `{"status": "error", "message": "..."}`

#### `/api/device/mode` (POST)
- **Purpose**: Get current device mode and class information
- **Payload**: `{"device_id": "ESP32-01"}`
- **Response**: `{"mode": "attendance", "class_name": "Physics 101", ...}`

#### `/api/device/poll` (POST)
- **Purpose**: Check for pending enrollment/deletion commands
- **Payload**: `{"device_id": "ESP32-01"}`
- **Response**: `{"has_command": true, "id": 1, "command_type": "enroll", "fingerprint_id": 5, "student_name": "Jane Smith"}`

#### `/api/device/command/<id>/complete` (POST)
- **Purpose**: Report command completion status
- **Payload**: `{"status": "completed"}` or `{"status": "failed"}`
- **Response**: `{"message": "Command completed"}`

#### `/api/students/by-fingerprint/<id>` (GET)
- **Purpose**: Get student information by fingerprint ID
- **Response**: `{"id": 1, "name": "John Doe", "fingerprint_id": 1, ...}`

### 3. **Improved JSON Parsing**
All JSON parsing now includes:
- Position validation before substring operations
- Bounds checking: `if (pos > threshold && end > pos && end <= length())`
- Graceful error handling when fields are missing
- Debug logging for troubleshooting

### 4. **Status Handling**
The script now correctly handles all backend response statuses:
- ✅ `"success"` - Attendance marked successfully
- ✅ `"duplicate"` - Already marked (treated as success with different message)
- ❌ `"error"` - Various errors (student not found, no active class, etc.)

### 5. **Better User Feedback**
- Clear LCD messages for all scenarios
- Appropriate LED indicators (green for success, red for errors)
- Detailed Serial debug output for troubleshooting
- WiFi status monitoring with auto-reconnect

## Configuration

### Update Server URL
Before uploading to your ESP32, update the server URL in the script:

```cpp
const char* serverURL = "http://YOUR_COMPUTER_IP:8888";
```

**How to find your computer's IP:**
- Linux/Mac: `hostname -I` or `ifconfig`
- Windows: `ipconfig`
- ⚠️ **Do NOT use** `127.0.0.1` or `localhost` - ESP32 needs your actual network IP

### WiFi Credentials
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### Device ID
```cpp
const char* DEVICE_ID = "ESP32-01"; // Must match device in database
```

## Testing the Integration

### 1. Start Flask Backend
```bash
cd /home/raju/fingerprint-module/final-backend
source venv/bin/activate
python3 app.py
```

The server should start on `http://0.0.0.0:8888`

### 2. Test Backend API
```bash
# Health check
curl http://localhost:8888/api/health

# Check device mode
curl -X POST http://localhost:8888/api/device/mode \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32-01"}'

# List students
curl http://localhost:8888/api/students/
```

### 3. Upload Arduino Script
1. Open `script.ino` in Arduino IDE
2. Select board: **ESP32 Dev Module**
3. Configure WiFi and server URL
4. Upload to ESP32
5. Open Serial Monitor (115200 baud)

### 4. Monitor Serial Output
You should see:
```
=== FINGERPRINT ATTENDANCE SYSTEM ===
Device ID: ESP32-01
Server: http://YOUR_IP:8888
WiFi Connected!
IP Address: 192.168.x.x
AS608 sensor connected!
Templates in sensor: X
=== SYSTEM READY ===
```

### 5. Test Attendance Flow

#### From Web Dashboard:
1. Navigate to `http://YOUR_IP:8888/`
2. Add a student with fingerprint ID (e.g., 1)
3. Set device mode to "Enrollment"
4. The ESP32 will poll and execute enrollment
5. Enroll the fingerprint when prompted
6. Set device mode to "Attendance" and select a class
7. Touch the sensor - attendance will be marked

#### From ESP32:
1. Touch the sensor when in Attendance mode
2. LCD shows "Place finger on sensor..."
3. After scan: "Welcome! [Student Name]"
4. Attendance is sent to backend
5. Check attendance records in dashboard

## Troubleshooting

### ESP32 Can't Connect to Server
- ✅ Verify server is running: `curl http://localhost:8888/api/health`
- ✅ Check firewall allows port 8888
- ✅ Ensure server binds to `0.0.0.0` not `127.0.0.1`
- ✅ Confirm ESP32 and computer are on same network
- ✅ Use actual IP address, not localhost

### Student Not Found Error
- ✅ Add student in web dashboard first
- ✅ Ensure fingerprint_id matches the one in sensor
- ✅ Check enrollment was successful

### Duplicate Attendance
- ✅ Normal behavior - backend prevents duplicates within 5 minutes
- ✅ Student sees "Already marked!" message

### WiFi Disconnection
- ✅ ESP32 auto-reconnects (checks every 30 seconds)
- ✅ If reconnect fails, ESP32 restarts automatically

### JSON Parsing Errors
- ✅ All parsing has bounds checking - check Serial output
- ✅ Enable DEBUG output to see raw responses

## Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   ESP32     │  HTTP   │    Flask     │         │   SQLite     │
│  + AS608    │ ◄─────► │   Backend    │ ◄─────► │   Database   │
│  Sensor     │  JSON   │  (Port 8888) │         │              │
└─────────────┘         └──────────────┘         └──────────────┘
      │                        ▲
      │                        │
      │                  ┌─────┴──────┐
      └──────────────────│  Teacher   │
         Touch to Scan   │  Dashboard │
                        │ (Browser)  │
                        └────────────┘
```

### Flow:
1. **Enrollment**: Teacher creates command via dashboard → ESP32 polls → Executes enrollment
2. **Attendance**: Student touches sensor → ESP32 scans → Sends to backend → Backend validates & saves
3. **Monitoring**: Dashboard shows real-time attendance, device status, statistics

## Key Features

✅ **Automatic Mode Switching** - Device polls backend every 5 seconds for mode changes
✅ **Command Queue** - Enrollment/deletion commands executed automatically
✅ **Duplicate Prevention** - Backend prevents duplicate attendance within 5 minutes
✅ **WiFi Auto-Recovery** - Automatic reconnection with health monitoring
✅ **Comprehensive Error Handling** - Graceful handling of network/server errors
✅ **Real-time Feedback** - LCD, LEDs, and buzzer provide instant feedback
✅ **Debug Logging** - Detailed Serial output for troubleshooting

## Next Steps

1. ✅ Script is ready - just update WiFi and server URL
2. ✅ Ensure Flask server is running
3. ✅ Add students through web dashboard
4. ✅ Upload script to ESP32
5. ✅ Test enrollment and attendance flows
6. 🎯 Deploy in production!

## Support

If you encounter issues:
1. Check Serial Monitor output (115200 baud)
2. Verify backend logs: Watch terminal running `python3 app.py`
3. Test API endpoints directly with curl
4. Ensure WiFi and network connectivity
5. Verify device exists in database with correct ID

---

**Updated**: November 15, 2025
**Version**: 3.1 - Enhanced Backend Integration
