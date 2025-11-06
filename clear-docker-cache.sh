#!/bin/bash
# Clear all Docker cache and rebuild from scratch

set -e

echo "🧹 Clearing Docker Cache and Rebuilding"
echo "=========================================="
echo ""

# Stop all running containers
echo "1️⃣  Stopping all EASM containers..."
docker compose -f docker-compose.tier-c.yml down 2>/dev/null || true
docker compose -f docker-compose.tier-b.yml down 2>/dev/null || true
docker compose -f docker-compose.tier-a.yml down 2>/dev/null || true

echo ""

# Remove EASM images
echo "2️⃣  Removing EASM images..."
docker images | grep -E "easm|tier" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

echo ""

# Remove dangling images
echo "3️⃣  Removing dangling images..."
docker image prune -f

echo ""

# Clear build cache
echo "4️⃣  Clearing build cache..."
docker builder prune -af

echo ""

# Show current state
echo "5️⃣  Current Docker state:"
echo "   Images:"
docker images | grep -E "REPOSITORY|easm|tier" || echo "   No EASM images found (good!)"

echo ""
echo "✅ Cache cleared successfully!"
echo ""
echo "📦 Now rebuild with:"
echo "   docker compose -f docker-compose.tier-c.yml build --no-cache"
echo "   OR"
echo "   ./deploy-tier-c.sh"
echo ""
