#!/bin/bash
# Troubleshoot authentication issues

set -e

echo "🔍 EASM Authentication Troubleshooting"
echo "======================================"
echo ""

# Check if backend is running
echo "1️⃣  Checking backend status..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is NOT running"
    echo "   Fix: docker compose -f docker-compose.tier-c.yml ps"
    exit 1
fi

echo ""

# Initialize default user
echo "2️⃣  Initializing default admin user..."
RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/auth/init)
echo "   Response: $RESPONSE"

echo ""

# Test login
echo "3️⃣  Testing login with admin/admin123..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123")

echo "   Response: $LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "   ✅ Login successful!"
    echo ""
    echo "   Credentials confirmed:"
    echo "   Username: admin"
    echo "   Password: admin123"
else
    echo "   ❌ Login failed"
    echo ""
    echo "   Possible issues:"
    echo "   - User not created (run init endpoint first)"
    echo "   - Wrong credentials"
    echo "   - Database issue"
fi

echo ""

# Check if we can list users (without auth)
echo "4️⃣  Checking API accessibility..."
API_RESPONSE=$(curl -s http://localhost:8000/api/v1/users/ 2>&1)
if echo "$API_RESPONSE" | grep -q "Not authenticated"; then
    echo "   ✅ API is working (requires authentication as expected)"
elif echo "$API_RESPONSE" | grep -q "Internal Server Error"; then
    echo "   ❌ API has internal error"
else
    echo "   Response: $API_RESPONSE"
fi

echo ""
echo "======================================"
echo "✅ Troubleshooting complete"
echo ""
