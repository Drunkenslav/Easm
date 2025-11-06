#!/bin/bash
# Nuclear option - completely clear Docker and rebuild

set -e

echo "☢️  NUCLEAR DOCKER CACHE CLEAR"
echo "================================"
echo ""

# Pull latest code
echo "1️⃣  Pulling latest code from main..."
git checkout main
git pull origin main

echo ""

# Stop and remove ALL containers
echo "2️⃣  Stopping and removing ALL containers..."
docker compose -f docker-compose.tier-c.yml down -v 2>/dev/null || true
docker compose -f docker-compose.tier-b.yml down -v 2>/dev/null || true
docker compose -f docker-compose.tier-a.yml down -v 2>/dev/null || true

echo ""

# Remove ALL images related to EASM
echo "3️⃣  Removing ALL EASM-related images..."
docker images | grep -i easm | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
docker images | grep -i tier | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

echo ""

# Remove ALL dangling images
echo "4️⃣  Removing dangling images..."
docker image prune -af

echo ""

# Clear build cache completely
echo "5️⃣  Clearing ALL build cache..."
docker builder prune -af --all

echo ""

# Remove buildkit cache
echo "6️⃣  Removing buildkit cache..."
docker buildx prune -af 2>/dev/null || true

echo ""

# Show Docker is clean
echo "7️⃣  Verifying Docker is clean..."
echo ""
echo "Images:"
docker images | head -5
echo ""
echo "Build cache:"
docker system df
echo ""

echo "✅ Docker is now completely clean!"
echo ""
echo "🚀 Now rebuilding from absolute scratch..."
echo ""

# Build with no cache whatsoever
docker compose -f docker-compose.tier-c.yml build --no-cache --pull

echo ""
echo "✅ Build complete! Starting services..."
echo ""

# Start services with scaling
docker compose -f docker-compose.tier-c.yml up -d \
    --scale backend=2 \
    --scale frontend=2 \
    --scale celery-worker=3

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service status:"
docker compose -f docker-compose.tier-c.yml ps
echo ""
