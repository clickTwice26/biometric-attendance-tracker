#include <HardwareSerial.h>
#include <Adafruit_Fingerprint.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <EEPROM.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ================== WIFI & SERVER CREDENTIALS ==================
const char* ssid = "Saif12";
const char* password = "00000000";
const char* serverURL = "http://156.67.110.215:8888"; // Your Flask server IP:port
// Note: If running locally, use your computer's local IP (not 127.0.0.1)
// Find IP with: hostname -I (Linux/Mac) or ipconfig (Windows)

// ================== PIN DEFINITIONS ==================
#define TCH_PIN 4       // Touch detection pin
#define RXD2 16         // AS608 TX to ESP32 RX2
#define TXD2 17         // AS608 RX to ESP32 TX2
#define RED_LED 25
#define GREEN_LED 27
#define BUZZER 26

// ================== OBJECTS ==================
HardwareSerial mySerial(2);
Adafruit_Fingerprint finger(&mySerial);
LiquidCrystal_I2C* lcd = nullptr;
byte lcdAddress = 0x27;

// ================== DEVICE CONFIGURATION ==================
const char* DEVICE_ID = "ESP32-01"; // Unique device identifier

// ================== DEBUG MACROS ==================
#define DEBUG_PRINT(...)   Serial.print(__VA_ARGS__)
#define DEBUG_PRINTLN(...) Serial.println(__VA_ARGS__)

// ================== UTILITIES ==================
void beep(int timeMs) {
  digitalWrite(BUZZER, HIGH);
  delay(timeMs);
  digitalWrite(BUZZER, LOW);
}

void indicateSuccess() {
  digitalWrite(GREEN_LED, HIGH);
  beep(100);
  delay(100);
  digitalWrite(GREEN_LED, LOW);
}

void indicateFailure() {
  digitalWrite(RED_LED, HIGH);
  beep(300);
  delay(200);
  digitalWrite(RED_LED, LOW);
}

void showLCD(const String &line1, const String &line2 = "") {
  if (lcd == nullptr) return;
  lcd->clear();
  lcd->setCursor(0, 0);
  // Safely print line1 with bounds checking
  if (line1.length() > 16) {
    lcd->print(line1.substring(0, 16));
  } else {
    lcd->print(line1);
  }
  lcd->setCursor(0, 1);
  // Safely print line2 with bounds checking
  if (line2.length() > 16) {
    lcd->print(line2.substring(0, 16));
  } else {
    lcd->print(line2);
  }
}

// ================== SERIAL INPUT WITH TIMEOUT ==================
String readSerialLine(uint32_t timeoutMs = 15000) {
  String s = "";
  uint32_t start = millis();
  while (millis() - start < timeoutMs) {
    if (Serial.available()) {
      char c = Serial.read();
      if (c == '\r' || c == '\n') {
        if (s.length() > 0) break;
      } else {
        s += c;
      }
    }
  }
  s.trim();
  DEBUG_PRINTLN("<< INPUT: \"" + s + "\"");
  return s;
}

// ================== I2C LCD SCANNER ==================
bool initLCD() {
  byte addresses[] = {0x27, 0x3F};
  for (byte addr : addresses) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      lcdAddress = addr;
      if (lcd != nullptr) {
        delete lcd;
      }
      lcd = new LiquidCrystal_I2C(addr, 16, 2);
      lcd->init();
      lcd->backlight();
      DEBUG_PRINTLN("LCD found at 0x" + String(addr, HEX));
      return true;
    }
  }
  DEBUG_PRINTLN("LCD not found! Check wiring.");
  return false;
}

// ================== WIFI SETUP ==================
const char* wlStatusToString(wl_status_t status) {
  switch (status) {
    case WL_IDLE_STATUS: return "WL_IDLE_STATUS";
    case WL_NO_SSID_AVAIL: return "WL_NO_SSID_AVAIL";
    case WL_SCAN_COMPLETED: return "WL_SCAN_COMPLETED";
    case WL_CONNECTED: return "WL_CONNECTED";
    case WL_CONNECT_FAILED: return "WL_CONNECT_FAILED";
    case WL_CONNECTION_LOST: return "WL_CONNECTION_LOST";
    case WL_DISCONNECTED: return "WL_DISCONNECTED";
    default: return "UNKNOWN_STATUS";
  }
}

void setupWiFi() {
  DEBUG_PRINTLN("\nConnecting to WiFi...");
  showLCD("Connecting to", ssid);
  
  WiFi.disconnect(true);
  delay(100);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);
  
  DEBUG_PRINTLN("Attempting to connect to SSID: '" + String(ssid) + "'");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  wl_status_t lastStatus = WL_IDLE_STATUS;

  while (WiFi.status() != WL_CONNECTED) {
    wl_status_t currentStatus = WiFi.status();
    if (currentStatus != lastStatus) {
      DEBUG_PRINTLN("WiFi Status: " + String(wlStatusToString(currentStatus)));
      lastStatus = currentStatus;
    }
    
    delay(500);
    DEBUG_PRINT(".");
    if (lcd != nullptr) lcd->print(".");
    attempts++;
    
    if (attempts > 40) {
      DEBUG_PRINTLN("\nFailed to connect after 40 attempts.");
      DEBUG_PRINTLN("Final WiFi Status: " + String(wlStatusToString(WiFi.status())));
      showLCD("WiFi Failed!", "Restarting...");
      delay(3000);
      ESP.restart(); // Restart ESP32 if WiFi fails
    }
  }

  DEBUG_PRINTLN("\nWiFi Connected!");
  DEBUG_PRINTLN("IP Address: " + WiFi.localIP().toString());
  DEBUG_PRINTLN("Signal Strength (RSSI): " + String(WiFi.RSSI()) + " dBm");
  showLCD("WiFi Connected!", WiFi.localIP().toString());
  delay(2000);
}

bool ensureWiFiConnection() {
  if (WiFi.status() == WL_CONNECTED) {
    return true;
  }
  
  DEBUG_PRINTLN("WiFi disconnected! Reconnecting...");
  showLCD("WiFi Lost", "Reconnecting...");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    DEBUG_PRINTLN("WiFi reconnected!");
    showLCD("WiFi OK", WiFi.localIP().toString());
    delay(1000);
    return true;
  }
  
  DEBUG_PRINTLN("WiFi reconnection failed, restarting ESP32...");
  showLCD("WiFi Failed", "Restarting...");
  delay(2000);
  ESP.restart();
  return false;
}

// ================== HTTP HELPER FUNCTIONS ==================
bool checkServerConnection() {
  if (!ensureWiFiConnection()) {
    return false;
  }
  
  HTTPClient http;
  String url = String(serverURL) + "/api/health";
  
  DEBUG_PRINTLN("Checking server: " + url);
  http.begin(url);
  http.setTimeout(5000); // 5 second timeout
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    DEBUG_PRINTLN("Server online!");
    http.end();
    return true;
  } else {
    DEBUG_PRINTLN("Server offline! Code: " + String(httpCode));
    http.end();
    return false;
  }
}

String getCurrentClassInfo() {
  // This function reuses the mode check response which already contains class info
  // No need for a separate HTTP request
  return "";  // Class info is now obtained directly from checkDeviceMode()
}

// Note: Enrollment and deletion are now handled through command polling
// Teacher uses web portal -> Creates command -> ESP32 polls and executes

String httpGetStudentName(uint8_t fingerprintId) {
  if (!ensureWiFiConnection()) return "";
  
  HTTPClient http;
  String url = String(serverURL) + "/api/students/by-fingerprint/" + String(fingerprintId);
  
  http.begin(url);
  http.setTimeout(5000);
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String response = http.getString();
    DEBUG_PRINTLN("Student data: " + response);
    
    // Parse "name" from JSON with comprehensive bounds checking
    int namePos = response.indexOf("\"name\"");
    if (namePos > -1 && namePos < response.length() - 10) {
      int colonPos = response.indexOf(":", namePos);
      if (colonPos > -1 && colonPos < response.length() - 3) {
        int openQuotePos = response.indexOf("\"", colonPos);
        if (openQuotePos > -1 && openQuotePos < response.length() - 1) {
          int closeQuotePos = response.indexOf("\"", openQuotePos + 1);
          if (closeQuotePos > openQuotePos && closeQuotePos <= response.length()) {
            String name = response.substring(openQuotePos + 1, closeQuotePos);
            http.end();
            return name;
          }
        }
      }
    }
  } else {
    DEBUG_PRINTLN("Failed to get student: " + String(httpCode));
  }
  
  http.end();
  return "";
}

bool httpMarkAttendance(uint8_t fingerprintId, bool success) {
  if (WiFi.status() != WL_CONNECTED) return false;
  
  HTTPClient http;
  String url = String(serverURL) + "/api/attendance/mark";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  String status = success ? "present" : "absent";
  String payload = "{\"fingerprint_id\":" + String(fingerprintId) + 
                   ",\"status\":\"" + status + 
                   "\",\"device_id\":\"" + String(DEVICE_ID) + "\"}";
  
  DEBUG_PRINTLN("POST " + url);
  DEBUG_PRINTLN("Payload: " + payload);
  
  int httpCode = http.POST(payload);
  String response = http.getString();
  DEBUG_PRINTLN("Mark attendance response: " + String(httpCode));
  DEBUG_PRINTLN("Response: " + response);
  
  http.end();
  return (httpCode == 201 || httpCode == 200);
}

// ================== OLD FUNCTIONS (No longer used - now using polling) ==================
// These functions are kept for reference but not called in polling mode
/*
uint8_t enrollUser() {
  // This function is deprecated - enroll via Teacher Portal instead
  // ESP32 will automatically receive and execute enrollment commands
}
*/

// ================== TEMPLATE EXTRACTION HELPER ==================
// Note: Template data is in sensor's CharBuffer after createModel()
// We'll use a simpler approach: store model in sensor temporarily, 
// then use loadModel to read it back

// ================== SCAN AND SEND FINGERPRINT DATA ==================
bool scanAndSendFingerprint() {
  showLCD("Place finger", "on sensor...");
  DEBUG_PRINTLN("Waiting for finger...");
  
  // Wait for finger
  int p = -1;
  uint32_t start = millis();
  while (p != FINGERPRINT_OK && (millis() - start < 10000)) {
    p = finger.getImage();
    if (p == FINGERPRINT_NOFINGER) {
      delay(50);
      continue;
    }
    if (p != FINGERPRINT_OK) {
      DEBUG_PRINTLN("getImage() error: " + String(p));
      delay(50);
      continue;
    }
  }
  
  if (p != FINGERPRINT_OK) {
    showLCD("Timeout", "No finger");
    indicateFailure();
    delay(1500);
    return false;
  }
  
  showLCD("Reading...", "Please wait");
  
  // Convert image to template
  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) {
    showLCD("Read error", "Try again");
    indicateFailure();
    delay(1500);
    return false;
  }
  
  // Search fingerprint in sensor (local matching as fallback)
  p = finger.fingerFastSearch();
  
  if (p == FINGERPRINT_OK) {
    uint8_t fingerprintId = finger.fingerID;
    uint16_t confidence = finger.confidence;
    
    DEBUG_PRINTLN("Fingerprint found! ID: " + String(fingerprintId) + ", Confidence: " + String(confidence));
    
    // Send to server for verification and attendance
    if (sendFingerprintToServer(fingerprintId, confidence)) {
      return true;
    } else {
      showLCD("Server error", "Try again");
      indicateFailure();
      delay(1500);
      return false;
    }
  } else if (p == FINGERPRINT_NOTFOUND) {
    showLCD("Not found", "Contact teacher");
    indicateFailure();
    DEBUG_PRINTLN("Fingerprint not found in sensor");
    delay(2000);
    return false;
  } else {
    showLCD("Scan error", "Try again");
    indicateFailure();
    DEBUG_PRINTLN("fingerFastSearch() error: " + String(p));
    delay(1500);
    return false;
  }
}

bool sendFingerprintToServer(uint8_t fingerprintId, uint16_t confidence) {
  if (!ensureWiFiConnection()) {
    showLCD("WiFi Error", "Check connection");
    return false;
  }
  
  HTTPClient http;
  String url = String(serverURL) + "/api/attendance/verify";
  
  http.begin(url);
  http.setTimeout(10000);
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"fingerprint_id\":" + String(fingerprintId) + 
                   ",\"confidence\":" + String(confidence) +
                   ",\"device_id\":\"" + String(DEVICE_ID) + "\"}";
  
  DEBUG_PRINTLN("Sending fingerprint to server: " + payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 200 || httpCode == 201) {
    String response = http.getString();
    http.end();
    DEBUG_PRINTLN("Server response: " + response);
    
    // Parse "status" field from JSON
    int statusPos = response.indexOf("\"status\"");
    String status = "";
    if (statusPos > -1 && statusPos < response.length() - 10) {
      int colonPos = response.indexOf(":", statusPos);
      if (colonPos > -1 && colonPos < response.length() - 3) {
        int openQuotePos = response.indexOf("\"", colonPos);
        if (openQuotePos > -1 && openQuotePos < response.length() - 1) {
          int closeQuotePos = response.indexOf("\"", openQuotePos + 1);
          if (closeQuotePos > openQuotePos && closeQuotePos <= response.length()) {
            status = response.substring(openQuotePos + 1, closeQuotePos);
          }
        }
      }
    }
    
    // Parse "name" field
    int namePos = response.indexOf("\"name\"");
    String studentName = "";
    if (namePos > -1 && namePos < response.length() - 10) {
      int colonPos = response.indexOf(":", namePos);
      if (colonPos > -1 && colonPos < response.length() - 3) {
        int openQuotePos = response.indexOf("\"", colonPos);
        if (openQuotePos > -1 && openQuotePos < response.length() - 1) {
          int closeQuotePos = response.indexOf("\"", openQuotePos + 1);
          if (closeQuotePos > openQuotePos && closeQuotePos <= response.length()) {
            studentName = response.substring(openQuotePos + 1, closeQuotePos);
          }
        }
      }
    }
    
    // Parse "message" field
    int msgPos = response.indexOf("\"message\"");
    String message = "";
    if (msgPos > -1 && msgPos < response.length() - 12) {
      int colonPos = response.indexOf(":", msgPos);
      if (colonPos > -1 && colonPos < response.length() - 3) {
        int openQuotePos = response.indexOf("\"", colonPos);
        if (openQuotePos > -1 && openQuotePos < response.length() - 1) {
          int closeQuotePos = response.indexOf("\"", openQuotePos + 1);
          if (closeQuotePos > openQuotePos && closeQuotePos <= response.length()) {
            message = response.substring(openQuotePos + 1, closeQuotePos);
          }
        }
      }
    }
    
    DEBUG_PRINTLN("Parsed status: " + status);
    DEBUG_PRINTLN("Parsed name: " + studentName);
    DEBUG_PRINTLN("Parsed message: " + message);
    
    // Handle success response
    if (status == "success") {
      if (studentName.length() > 0) {
        String displayName = studentName.substring(0, min(16, (int)studentName.length()));
        showLCD("Welcome!", displayName);
      } else {
        showLCD("Attendance", "Marked!");
      }
      indicateSuccess();
      delay(2000);
      
      // Display message if present
      if (message.length() > 0) {
        String line1 = message.substring(0, min(16, (int)message.length()));
        String line2 = "";
        if (message.length() > 16) {
          line2 = message.substring(16, min(32, (int)message.length()));
        }
        showLCD(line1, line2);
        delay(2000);
      }
      return true;
    }
    // Handle duplicate attendance
    else if (status == "duplicate") {
      showLCD("Already marked!", studentName.substring(0, min(16, (int)studentName.length())));
      indicateSuccess(); // Still a success, just duplicate
      delay(2000);
      return true;
    }
    // Handle error response
    else if (status == "error") {
      if (message.length() > 0) {
        String line1 = message.substring(0, min(16, (int)message.length()));
        String line2 = "";
        if (message.length() > 16) {
          line2 = message.substring(16, min(32, (int)message.length()));
        }
        showLCD(line1, line2);
      } else {
        showLCD("Error", "Contact teacher");
      }
      indicateFailure();
      delay(2000);
      return false;
    }
    // Unknown status
    else {
      showLCD("Unknown status", status.substring(0, min(16, (int)status.length())));
      indicateFailure();
      delay(2000);
      return false;
    }
  }
  // Handle 404 - Student not found
  else if (httpCode == 404) {
    String response = http.getString();
    http.end();
    DEBUG_PRINTLN("Student not found: " + response);
    showLCD("Not registered", "Contact teacher");
    indicateFailure();
    delay(2000);
    return false;
  }
  // Handle other HTTP errors
  else {
    DEBUG_PRINTLN("Server error: " + String(httpCode));
    if (httpCode > 0) {
      String response = http.getString();
      DEBUG_PRINTLN("Error response: " + response);
    }
    http.end();
    showLCD("Server Error", "Code: " + String(httpCode));
    indicateFailure();
    delay(2000);
    return false;
  }
}

/*
void deleteUser() {
  // This function is deprecated - delete via Teacher Portal instead
  // ESP32 will automatically receive and execute deletion commands
}
*/

// ================== SETUP ==================
void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  DEBUG_PRINTLN("\n\n=== FINGERPRINT ATTENDANCE SYSTEM ===");
  DEBUG_PRINTLN("Device ID: " + String(DEVICE_ID));
  DEBUG_PRINTLN("Server: " + String(serverURL));
  DEBUG_PRINTLN("Version: 3.0 - Polling-Based Listening Device");
  DEBUG_PRINTLN("Mode: Automatic - No manual commands required");

  mySerial.begin(57600, SERIAL_8N1, RXD2, TXD2);
  Wire.begin();

  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(TCH_PIN, INPUT);

  // Initialize LCD
  showLCD("Init LCD...", "");
  if (!initLCD()) {
    showLCD("LCD Error", "Check I2C");
    while (1) delay(100);
  }

  // Connect to WiFi
  setupWiFi();
  
  // Check server connection
  showLCD("Checking server");
  if (checkServerConnection()) {
    showLCD("Server OK!", "");
    delay(1500);
  } else {
    showLCD("Server offline", "Retrying...");
    delay(2000);
  }

  // Initialize Fingerprint Sensor
  showLCD("Sensor check...", "");
  finger.begin(57600);
  if (finger.verifyPassword()) {
    DEBUG_PRINTLN("AS608 sensor connected!");
    finger.getTemplateCount();
    DEBUG_PRINTLN("Templates in sensor: " + String(finger.templateCount));
  } else {
    showLCD("Sensor fail!", "Check wiring");
    DEBUG_PRINTLN("AS608 not found!");
    while (1) delay(100);
  }

  showLCD("Listening...", "Touch to scan");
  DEBUG_PRINTLN("\n=== SYSTEM READY ===");
  DEBUG_PRINTLN("Mode: Automatic polling every 5 seconds");
  DEBUG_PRINTLN("Touch sensor to mark attendance");
  DEBUG_PRINTLN("Teacher Portal: " + String(serverURL));
  DEBUG_PRINTLN("Device will auto-execute enroll/delete commands from server");
}

// ================== DEVICE MODE CHECKING ==================
String currentMode = "idle";  // 'idle', 'enrollment', 'attendance'
String currentClassName = "";  // Current class name
unsigned long lastModeCheck = 0;
const unsigned long MODE_CHECK_INTERVAL = 5000; // Check mode every 5 seconds

// Global variable to store template during enrollment
String lastEnrollmentTemplate = "";

// Forward declarations
bool executeEnrollCommand(uint8_t id, const String &name);
bool executeDeleteCommand(uint8_t id);
void reportCommandCompletion(int commandId, bool success, String templateData = "");

String checkDeviceMode() {
  if (!ensureWiFiConnection()) {
    DEBUG_PRINTLN("WiFi not connected, cannot check mode");
    return "idle";
  }
  
  HTTPClient http;
  String url = String(serverURL) + "/api/device/mode";
  
  http.begin(url);
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"device_id\":\"" + String(DEVICE_ID) + "\"}";
  
  int httpCode = http.POST(payload);
  
  if (httpCode != 200) {
    DEBUG_PRINTLN("Mode check failed: " + String(httpCode));
    http.end();
    return currentMode; // Keep current mode on error
  }
  
  String response = http.getString();
  http.end();
  
  DEBUG_PRINTLN("Mode check response: " + response);
  
  // Parse mode from response with comprehensive bounds checking
  int modePos = response.indexOf("\"mode\"");
  if (modePos == -1 || modePos >= response.length() - 10) {
    DEBUG_PRINTLN("ERROR: 'mode' not found in response");
    return currentMode;
  }
  
  // Find the colon after "mode"
  int colonPos = response.indexOf(":", modePos);
  if (colonPos == -1 || colonPos >= response.length() - 3) {
    DEBUG_PRINTLN("ERROR: ':' not found after 'mode'");
    return currentMode;
  }
  
  // Find the opening quote after the colon
  int openQuotePos = response.indexOf("\"", colonPos);
  if (openQuotePos == -1 || openQuotePos >= response.length() - 1) {
    DEBUG_PRINTLN("ERROR: opening quote not found");
    return currentMode;
  }
  
  // Find the closing quote
  int closeQuotePos = response.indexOf("\"", openQuotePos + 1);
  if (closeQuotePos == -1 || closeQuotePos > response.length()) {
    DEBUG_PRINTLN("ERROR: closing quote not found");
    return currentMode;
  }
  
  String mode = response.substring(openQuotePos + 1, closeQuotePos);
  
  // Also extract class_name if present (for attendance mode)
  int classNamePos = response.indexOf("\"class_name\"");
  currentClassName = "";
  if (classNamePos > -1 && classNamePos < response.length() - 20) {
    int colonPos = response.indexOf(":", classNamePos);
    if (colonPos > -1 && colonPos < response.length() - 3) {
      int openQuotePos2 = response.indexOf("\"", colonPos);
      if (openQuotePos2 > -1 && openQuotePos2 < response.length() - 1) {
        int closeQuotePos2 = response.indexOf("\"", openQuotePos2 + 1);
        if (closeQuotePos2 > openQuotePos2 && closeQuotePos2 <= response.length()) {
          currentClassName = response.substring(openQuotePos2 + 1, closeQuotePos2);
          DEBUG_PRINTLN("Current class: " + currentClassName);
        }
      }
    }
  }
  
  DEBUG_PRINTLN("=== DEVICE MODE: " + mode + " ===");
  
  return mode;
}

// ================== DEVICE POLLING ==================
bool pollForCommands() {
  if (!ensureWiFiConnection()) {
    DEBUG_PRINTLN("WiFi not connected, skipping poll");
    return false;
  }
  
  HTTPClient http;
  String url = String(serverURL) + "/api/device/poll";
  
  http.begin(url);
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"device_id\":\"" + String(DEVICE_ID) + "\"}";
  
  int httpCode = http.POST(payload);
  
  if (httpCode != 200) {
    DEBUG_PRINTLN("Poll failed: " + String(httpCode));
    http.end();
    return false;
  }
  
  String response = http.getString();
  http.end();
  
  DEBUG_PRINTLN("Poll response: " + response);
  
  // Parse JSON response to check if there's a command
  // Look for "has_command": true (with or without space)
  int hasCommandPos = response.indexOf("\"has_command\"");
  if (hasCommandPos == -1) {
    DEBUG_PRINTLN("No has_command field found");
    return false;
  }
  
  // Check if the value is true
  int truePos = response.indexOf("true", hasCommandPos);
  int falsePos = response.indexOf("false", hasCommandPos);
  
  // If false comes before true, or true is not found, no command
  if (truePos == -1 || (falsePos != -1 && falsePos < truePos)) {
    DEBUG_PRINTLN("has_command is false");
    return false; // No pending commands
  }
  
  // Extract command ID with bounds checking (handle pretty-printed JSON)
  int idPos = response.indexOf("\"id\"");
  int commandId = 0;
  if (idPos > -1 && idPos < response.length() - 10) {
    int colonPos = response.indexOf(":", idPos);
    if (colonPos > -1 && colonPos < response.length() - 2) {
      // Skip whitespace after colon
      int numStart = colonPos + 1;
      while (numStart < response.length() && (response.charAt(numStart) == ' ' || response.charAt(numStart) == '\n' || response.charAt(numStart) == '\r')) {
        numStart++;
      }
      // Find end of number
      int numEnd = numStart;
      while (numEnd < response.length() && response.charAt(numEnd) >= '0' && response.charAt(numEnd) <= '9') {
        numEnd++;
      }
      if (numEnd > numStart) {
        commandId = response.substring(numStart, numEnd).toInt();
      }
    }
  }
  
  if (commandId == 0) {
    DEBUG_PRINTLN("ERROR: Failed to parse command ID");
    return false;
  }
  
  // Extract command type with bounds checking (handle pretty-printed JSON)
  int typePos = response.indexOf("\"command_type\"");
  String commandType = "";
  if (typePos > -1 && typePos < response.length() - 20) {
    int colonPos = response.indexOf(":", typePos);
    if (colonPos > -1 && colonPos < response.length() - 3) {
      int openQuotePos = response.indexOf("\"", colonPos);
      if (openQuotePos > -1 && openQuotePos < response.length() - 1) {
        int closeQuotePos = response.indexOf("\"", openQuotePos + 1);
        if (closeQuotePos > openQuotePos && closeQuotePos <= response.length()) {
          commandType = response.substring(openQuotePos + 1, closeQuotePos);
        }
      }
    }
  }
  
  if (commandType.length() == 0) {
    DEBUG_PRINTLN("ERROR: Failed to parse command type");
    return false;
  }
  
  // Extract fingerprint ID with bounds checking (handle pretty-printed JSON)
  int fpIdPos = response.indexOf("\"fingerprint_id\"");
  int fingerprintId = 0;
  if (fpIdPos > -1 && fpIdPos < response.length() - 20) {
    int colonPos = response.indexOf(":", fpIdPos);
    if (colonPos > -1 && colonPos < response.length() - 2) {
      // Skip whitespace after colon
      int numStart = colonPos + 1;
      while (numStart < response.length() && (response.charAt(numStart) == ' ' || response.charAt(numStart) == '\n' || response.charAt(numStart) == '\r')) {
        numStart++;
      }
      // Find end of number (comma, newline, or closing brace)
      int numEnd = numStart;
      while (numEnd < response.length() && response.charAt(numEnd) >= '0' && response.charAt(numEnd) <= '9') {
        numEnd++;
      }
      if (numEnd > numStart) {
        fingerprintId = response.substring(numStart, numEnd).toInt();
      }
    }
  }
  
  // Extract student name with bounds checking (handle pretty-printed JSON)
  int namePos = response.indexOf("\"student_name\"");
  String studentName = "";
  if (namePos > -1 && namePos < response.length() - 20) {
    int colonPos = response.indexOf(":", namePos);
    if (colonPos > -1 && colonPos < response.length() - 3) {
      int openQuotePos = response.indexOf("\"", colonPos);
      if (openQuotePos > -1 && openQuotePos < response.length() - 1) {
        int closeQuotePos = response.indexOf("\"", openQuotePos + 1);
        if (closeQuotePos > openQuotePos && closeQuotePos <= response.length()) {
          studentName = response.substring(openQuotePos + 1, closeQuotePos);
        }
      }
    }
  }
  
  DEBUG_PRINTLN("=== COMMAND RECEIVED ===");
  DEBUG_PRINTLN("Command ID: " + String(commandId));
  DEBUG_PRINTLN("Type: " + commandType);
  DEBUG_PRINTLN("Fingerprint ID: " + String(fingerprintId));
  DEBUG_PRINTLN("Student: " + studentName);
  
  // Execute command
  bool success = false;
  
  if (commandType == "enroll") {
    showLCD("Enroll: " + studentName, "ID: " + String(fingerprintId));
    lastEnrollmentTemplate = "";  // Reset
    success = executeEnrollCommand(fingerprintId, studentName);
    
    // Report completion with template data
    reportCommandCompletion(commandId, success, lastEnrollmentTemplate);
  } else if (commandType == "delete") {
    showLCD("Delete: " + studentName, "ID: " + String(fingerprintId));
    success = executeDeleteCommand(fingerprintId);
    
    // Report completion without template
    reportCommandCompletion(commandId, success, "");
  }
  
  return true;
}

bool executeEnrollCommand(uint8_t id, const String &name) {
  DEBUG_PRINTLN("\n=== EXECUTING ENROLL COMMAND ===");
  DEBUG_PRINTLN("ID: " + String(id) + ", Name: " + name);
  
  showLCD("Place finger", "to enroll...");
  
  int p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    delay(100);
  }
  
  indicateSuccess();
  showLCD("Hold still...");
  delay(500);
  
  p = finger.image2Tz(1);
  if (p != FINGERPRINT_OK) {
    showLCD("Image convert", "FAILED!");
    indicateFailure();
    return false;
  }
  
  showLCD("Remove finger");
  delay(2000);
  
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }
  
  showLCD("Place SAME", "finger again");
  delay(1000);
  
  p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    delay(100);
  }
  
  indicateSuccess();
  showLCD("Processing...");
  delay(500);
  
  p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK) {
    showLCD("Image convert", "FAILED!");
    indicateFailure();
    return false;
  }
  
  p = finger.createModel();
  if (p != FINGERPRINT_OK) {
    showLCD("Match FAILED!", "Try again");
    indicateFailure();
    return false;
  }
  
  // Store in sensor at specified ID (hybrid approach)
  showLCD("Storing...", "in sensor");
  
  p = finger.storeModel(id);
  if (p != FINGERPRINT_OK) {
    showLCD("Store FAILED!");
    indicateFailure();
    DEBUG_PRINTLN("Failed to store template: " + String(p));
    return false;
  }
  
  // Note: Template extraction not supported by Adafruit_Fingerprint library
  // Using hybrid approach: templates stored in sensor, server manages metadata
  lastEnrollmentTemplate = "";  // Empty since we can't extract
  
  showLCD("SUCCESS!", name);
  indicateSuccess();
  DEBUG_PRINTLN("Enrolled: " + name + " (ID " + String(id) + ")");
  DEBUG_PRINTLN("Template stored in sensor at ID " + String(id));
  delay(2000);
  
  return true;
}

bool executeDeleteCommand(uint8_t id) {
  DEBUG_PRINTLN("\n=== EXECUTING DELETE COMMAND ===");
  DEBUG_PRINTLN("Deleting ID: " + String(id));
  
  uint8_t p = finger.deleteModel(id);
  if (p == FINGERPRINT_OK) {
    showLCD("ID " + String(id), "Deleted!");
    indicateSuccess();
    DEBUG_PRINTLN("Deleted ID " + String(id));
    delay(2000);
    return true;
  } else {
    showLCD("Delete FAILED!", "ID: " + String(id));
    indicateFailure();
    DEBUG_PRINTLN("Delete failed with code: " + String(p));
    delay(2000);
    return false;
  }
}

void reportCommandCompletion(int commandId, bool success, String templateData) {
  if (!ensureWiFiConnection()) {
    DEBUG_PRINTLN("WiFi not connected, cannot report completion");
    return;
  }
  
  HTTPClient http;
  String url = String(serverURL) + "/api/device/command/" + String(commandId) + "/complete";
  
  DEBUG_PRINTLN("Reporting to: " + url);
  
  http.begin(url);
  http.setTimeout(15000);  // Longer timeout for template upload
  http.addHeader("Content-Type", "application/json");
  
  String status = success ? "completed" : "failed";
  String payload = "{\"status\":\"" + status + "\"";
  
  // Include template data if provided (for enrollment)
  if (templateData.length() > 0) {
    payload += ",\"template\":\"" + templateData + "\"";
    DEBUG_PRINTLN("Including template data (" + String(templateData.length()) + " chars)");
  }
  
  payload += "}";
  
  DEBUG_PRINTLN("Reporting completion: " + url);
  DEBUG_PRINTLN("Payload: " + payload);
  DEBUG_PRINTLN("Payload size: " + String(payload.length()) + " bytes");
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 200) {
    String response = http.getString();
    DEBUG_PRINTLN("Command marked as " + status);
    DEBUG_PRINTLN("Response: " + response);
  } else {
    DEBUG_PRINTLN("Failed to report completion: " + String(httpCode));
    if (httpCode > 0) {
      String response = http.getString();
      DEBUG_PRINTLN("Error response: " + response);
    } else if (httpCode == -11) {
      DEBUG_PRINTLN("HTTP Error -11: Connection timeout/refused. Check server availability.");
    } else {
      DEBUG_PRINTLN("HTTP client error code: " + String(httpCode));
    }
  }
  
  http.end();
}

// ================== LOOP ==================
void loop() {
  static bool lastTouch = false;
  static unsigned long lastTouchTime = 0;
  const unsigned long DEBOUNCE = 1000;
  static unsigned long lastEnrollmentPoll = 0;
  const unsigned long ENROLLMENT_POLL_INTERVAL = 2000; // Check for enrollment commands every 2 seconds

  // --- Check Device Mode Periodically ---
  if (millis() - lastModeCheck >= MODE_CHECK_INTERVAL) {
    lastModeCheck = millis();
    String newMode = checkDeviceMode();
    
    if (newMode != currentMode) {
      currentMode = newMode;
      
      // Update LCD based on mode
      if (currentMode == "enrollment") {
        showLCD("ENROLLMENT MODE", "Ready to enroll");
        DEBUG_PRINTLN("Switched to ENROLLMENT mode - will poll for commands");
        lastEnrollmentPoll = 0; // Trigger immediate poll
        
      } else if (currentMode == "attendance") {
        // Use currentClassName from mode check
        if (currentClassName.length() > 0) {
          String displayClass = currentClassName.substring(0, min(10, (int)currentClassName.length()));
          showLCD("Class: " + displayClass, "Touch to scan");
        } else {
          showLCD("ATTENDANCE MODE", "Touch to scan");
        }
        DEBUG_PRINTLN("Switched to ATTENDANCE mode - Class: " + currentClassName);
      } else {
        showLCD("Ready", "Touch to scan");
        DEBUG_PRINTLN("IDLE mode - Ready to scan");
      }
    }
  }

  // Class info is now updated automatically in checkDeviceMode()

  // --- ENROLLMENT MODE: Continuously check for enrollment commands ---
  if (currentMode == "enrollment") {
    if (millis() - lastEnrollmentPoll >= ENROLLMENT_POLL_INTERVAL) {
      lastEnrollmentPoll = millis();
      
      DEBUG_PRINTLN("Checking for enrollment commands...");
      bool commandExecuted = pollForCommands();
      
      if (commandExecuted) {
        // Command was executed, switch back to idle and check mode again
        DEBUG_PRINTLN("Enrollment command executed, rechecking mode...");
        delay(1000);
        currentMode = checkDeviceMode(); // Refresh mode immediately
        
        if (currentMode == "idle") {
          showLCD("Enrollment done", "Touch to scan");
          delay(2000);
        } else if (currentMode == "enrollment") {
          showLCD("ENROLLMENT MODE", "Ready to enroll");
        } else if (currentMode == "attendance") {
          if (currentClassName.length() > 0) {
            String displayClass = currentClassName.substring(0, min(10, (int)currentClassName.length()));
            showLCD("Class: " + displayClass, "Touch to scan");
          } else {
            showLCD("ATTENDANCE MODE", "Touch to scan");
          }
        }
      }
    }
  }
  
  // --- FINGER DETECTION: Check for finger on sensor (ALL MODES) ---
  // Method 1: Check touch pin (if connected)
  bool touchPin = (digitalRead(TCH_PIN) == HIGH);
  
  // Method 2: Check sensor directly for finger presence (more reliable)
  static unsigned long lastFingerCheck = 0;
  static bool fingerDetected = false;
  
  if (millis() - lastFingerCheck >= 200) { // Check every 200ms
    lastFingerCheck = millis();
    int p = finger.getImage();
    fingerDetected = (p == FINGERPRINT_OK);
    
    // Debug: Print status periodically
    static unsigned long lastDebug = 0;
    if (millis() - lastDebug >= 10000) { // Every 10 seconds
      lastDebug = millis();
      DEBUG_PRINTLN("Finger check: " + String(fingerDetected ? "DETECTED" : "None") + ", Touch pin: " + String(touchPin));
    }
  }
  
  // Trigger on either touch pin OR finger detected on sensor
  bool fingerPresent = touchPin || fingerDetected;
  
  // Improved debouncing: only trigger on rising edge after debounce period
  if (fingerPresent && !lastTouch && (millis() - lastTouchTime > DEBOUNCE)) {
    DEBUG_PRINTLN("===================================");
    DEBUG_PRINTLN("TOUCH DETECTED - Scanning fingerprint");
    DEBUG_PRINTLN("Current mode: " + currentMode);
    DEBUG_PRINTLN("===================================");
    
    // ALWAYS scan and send fingerprint to server - backend decides everything
    scanAndSendFingerprint();
    
    // Restore display based on current mode
    delay(500);
    if (currentMode == "attendance" && currentClassName.length() > 0) {
      String displayClass = currentClassName.substring(0, min(10, (int)currentClassName.length()));
      showLCD("Class: " + displayClass, "Touch to scan");
    } else if (currentMode == "attendance") {
      showLCD("ATTENDANCE MODE", "Touch to scan");
    } else if (currentMode == "enrollment") {
      showLCD("ENROLLMENT MODE", "Ready to enroll");
    } else {
      showLCD("Ready", "Touch to scan");
    }
    
    lastTouchTime = millis();
  }
  lastTouch = fingerPresent;
  
  // --- Monitor WiFi connection health ---
  static unsigned long lastWiFiCheck = 0;
  if (millis() - lastWiFiCheck >= 30000) { // Check every 30 seconds
    lastWiFiCheck = millis();
    if (WiFi.status() != WL_CONNECTED) {
      DEBUG_PRINTLN("WiFi health check failed, reconnecting...");
      ensureWiFiConnection();
    }
  }
}
