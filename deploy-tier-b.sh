#!/bin/bash
# Deploy EASM Platform - Tier B (Business Edition)
# Multi-container setup with PostgreSQL, Redis, and Celery workers

set -e

echo "🚀 Deploying EASM Platform - Tier B (Business Edition)"
echo "======================================================="
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
docker compose -f docker-compose.tier-b.yml build

echo ""
echo "🚀 Starting services..."
docker compose -f docker-compose.tier-b.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 15

echo ""
echo "📊 Service Status:"
docker compose -f docker-compose.tier-b.yml ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access Points:"
echo "   - Application: http://localhost"
echo "   - API Docs: http://localhost/docs"
echo "   - Backend (direct): http://localhost:8000"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker compose -f docker-compose.tier-b.yml logs -f"
echo "   - View worker logs: docker compose -f docker-compose.tier-b.yml logs -f celery-worker"
echo "   - Stop all: docker compose -f docker-compose.tier-b.yml down"
echo "   - Backup PostgreSQL: docker compose -f docker-compose.tier-b.yml exec postgres pg_dump -U easm easm > backup.sql"
echo ""
