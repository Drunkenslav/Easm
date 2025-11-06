#!/bin/bash
# Reset database and deploy with fresh admin user and mock data

set -e

echo "🔄 Resetting EASM Platform..."
echo "=============================="
echo ""

# Stop all containers
echo "1️⃣  Stopping containers..."
docker compose -f docker-compose.tier-c.yml down

echo ""

# Remove database volume to start fresh
echo "2️⃣  Removing old database..."
docker volume rm easm-data-tier-c 2>/dev/null || echo "   (No old volume found)"

echo ""

# Rebuild backend (has new init_db.py)
echo "3️⃣  Rebuilding backend with database initialization..."
docker compose -f docker-compose.tier-c.yml build backend

echo ""

# Start everything
echo "4️⃣  Starting all services..."
docker compose -f docker-compose.tier-c.yml up -d \
    --scale backend=2 \
    --scale frontend=2 \
    --scale celery-worker=3

echo ""

# Wait for backend to initialize
echo "5️⃣  Waiting for backend to initialize database..."
sleep 10

echo ""

# Check backend logs for initialization
echo "6️⃣  Backend initialization log:"
docker compose -f docker-compose.tier-c.yml logs backend | grep -A 20 "Initializing database" || echo "   (Checking logs...)"

echo ""
echo "=============================="
echo "✅ Deployment complete!"
echo ""
echo "🔐 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🌐 Access:"
echo "   Application: http://localhost"
echo "   API Docs: http://localhost/docs"
echo ""
echo "📊 Mock data created:"
echo "   - 7 assets"
echo "   - 7 scans"
echo "   - 15 vulnerabilities"
echo ""
