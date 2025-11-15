#!/bin/bash
# Backend Testing Script
# Run this to verify backend is working before connecting ESP32

echo "================================"
echo "Backend Integration Test Script"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Server URL
SERVER="http://localhost:8888"

echo -e "${YELLOW}Testing Backend Endpoints...${NC}\n"

# Test 1: Health Check
echo "1. Health Check"
response=$(curl -s -w "\n%{http_code}" $SERVER/api/health)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "   Response: $body"
else
    echo -e "${RED}✗ Health check failed (HTTP $http_code)${NC}"
    exit 1
fi
echo ""

# Test 2: Device Mode Check
echo "2. Device Mode Check (ESP32-01)"
response=$(curl -s -w "\n%{http_code}" -X POST $SERVER/api/device/mode \
    -H "Content-Type: application/json" \
    -d '{"device_id":"ESP32-01"}')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ Device mode check passed${NC}"
    echo "   Response: $body"
else
    echo -e "${RED}✗ Device mode check failed (HTTP $http_code)${NC}"
fi
echo ""

# Test 3: Poll for Commands
echo "3. Poll for Commands"
response=$(curl -s -w "\n%{http_code}" -X POST $SERVER/api/device/poll \
    -H "Content-Type: application/json" \
    -d '{"device_id":"ESP32-01"}')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ Command polling works${NC}"
    echo "   Response: $body"
else
    echo -e "${RED}✗ Command polling failed (HTTP $http_code)${NC}"
fi
echo ""

# Test 4: List Students
echo "4. List Students"
response=$(curl -s -w "\n%{http_code}" $SERVER/api/students/)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ Student listing works${NC}"
    student_count=$(echo "$body" | grep -o '"id"' | wc -l)
    echo "   Found $student_count students"
else
    echo -e "${RED}✗ Student listing failed (HTTP $http_code)${NC}"
fi
echo ""

# Test 5: Verify Fingerprint (will fail without student)
echo "5. Verify Fingerprint Endpoint (Testing with ID 999)"
response=$(curl -s -w "\n%{http_code}" -X POST $SERVER/api/attendance/verify \
    -H "Content-Type: application/json" \
    -d '{"fingerprint_id":999,"confidence":95,"device_id":"ESP32-01"}')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n1)

if [ "$http_code" == "404" ]; then
    echo -e "${GREEN}✓ Verify endpoint working (student not found is expected)${NC}"
    echo "   Response: $body"
else
    echo -e "${YELLOW}⚠ Verify endpoint returned HTTP $http_code${NC}"
    echo "   Response: $body"
fi
echo ""

# Summary
echo "================================"
echo -e "${GREEN}Backend Integration Test Complete!${NC}"
echo "================================"
echo ""
echo "Next Steps:"
echo "1. Add students via web dashboard: $SERVER/"
echo "2. Update ESP32 script with this server URL"
echo "3. Upload script to ESP32"
echo "4. Monitor Serial output (115200 baud)"
echo ""
echo "Your computer's IP addresses:"
hostname -I | tr ' ' '\n' | grep -v "^$"
echo ""
echo "Use one of these IPs (not 127.0.0.1) in your ESP32 script"
echo ""
