#!/bin/bash
# Deploy EASM Platform - Tier C (Enterprise Edition)
# This script properly deploys with multiple replicas

set -e

echo "🚀 Deploying EASM Platform - Tier C (Enterprise Edition)"
echo "==========================================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating one with default values..."
    echo "⚠️  IMPORTANT: Change these secrets before production deployment!"
    echo ""

    cat > .env <<EOF
# PostgreSQL
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Backend secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF

    echo "✅ Created .env file with generated secrets"
    echo ""
fi

# Load environment variables
source .env

echo "📦 Building images..."
docker-compose -f docker-compose.tier-c.yml build

echo ""
echo "🚀 Starting services with scaling..."
echo "   - Backend: 2 replicas"
echo "   - Frontend: 2 replicas"
echo "   - Celery Workers: 3 replicas (12 concurrent scans)"
echo ""

# Deploy with replicas
# Note: docker-compose doesn't support deploy.replicas in standalone mode
# Use --scale flag instead
docker-compose -f docker-compose.tier-c.yml up -d \
    --scale backend=2 \
    --scale frontend=2 \
    --scale celery-worker=3

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.tier-c.yml ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access Points:"
echo "   - Application: http://localhost"
echo "   - API Docs: http://localhost/docs"
echo "   - Flower (Celery monitoring): http://localhost:5555"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.tier-c.yml logs -f"
echo "   - Scale backend: docker-compose -f docker-compose.tier-c.yml up -d --scale backend=4"
echo "   - Scale workers: docker-compose -f docker-compose.tier-c.yml up -d --scale celery-worker=5"
echo "   - Stop all: docker-compose -f docker-compose.tier-c.yml down"
echo ""
