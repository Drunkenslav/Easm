#!/bin/bash
# Quick debug - show what's actually happening

echo "🔍 DEBUGGING AUTHENTICATION ISSUE"
echo "=================================="
echo ""

# Check if backend is running
echo "1️⃣  Backend containers:"
docker ps | grep backend || echo "❌ NO BACKEND RUNNING!"

echo ""
echo "2️⃣  Backend logs (last 50 lines):"
docker compose -f docker-compose.tier-c.yml logs --tail=50 backend

echo ""
echo "3️⃣  Check if database file exists:"
docker compose -f docker-compose.tier-c.yml exec backend ls -la /data/ 2>/dev/null || echo "❌ Cannot access backend"

echo ""
echo "4️⃣  Check if database has users:"
docker compose -f docker-compose.tier-c.yml exec backend sqlite3 /data/easm.db "SELECT username, email FROM users;" 2>/dev/null || echo "❌ Cannot query database"

echo ""
echo "5️⃣  Test init_db.py manually:"
docker compose -f docker-compose.tier-c.yml exec backend python init_db.py 2>/dev/null || echo "❌ init_db.py failed"

echo ""
echo "=================================="
