#!/bin/bash
# Check why backend is crashing

echo "🚨 BACKEND CRASH DIAGNOSIS"
echo "=========================="
echo ""

echo "1️⃣  Container status:"
docker compose -f docker-compose.tier-c.yml ps backend

echo ""
echo "2️⃣  Recent backend logs (last 100 lines):"
docker compose -f docker-compose.tier-c.yml logs --tail=100 backend

echo ""
echo "3️⃣  Check if start.sh exists and is executable:"
docker compose -f docker-compose.tier-c.yml exec backend ls -la start.sh 2>/dev/null || echo "❌ Can't check - container not running or restarting"

echo ""
echo "4️⃣  Check container restart count:"
docker ps -a | grep backend | grep -o "Restarting\|Up\|Exited"

echo ""
echo "=========================="
echo ""
echo "🔍 If you see 'Restarting' or many restarts, the backend is crash-looping!"
