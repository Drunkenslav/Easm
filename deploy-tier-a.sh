#!/bin/bash
# Deploy EASM Platform - Tier A (Open Source Edition)
# Minimal setup for individual users and small teams

set -e

echo "🚀 Deploying EASM Platform - Tier A (Open Source Edition)"
echo "=========================================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating one with default values..."
    echo "⚠️  IMPORTANT: Change these secrets before production deployment!"
    echo ""

    cat > .env <<EOF
# Backend secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF

    echo "✅ Created .env file with generated secrets"
    echo ""
fi

echo "📦 Building images..."
docker-compose -f docker-compose.tier-a.yml build

echo ""
echo "🚀 Starting services..."
docker-compose -f docker-compose.tier-a.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.tier-a.yml ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access Points:"
echo "   - Application: http://localhost"
echo "   - API Docs: http://localhost/docs"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.tier-a.yml logs -f"
echo "   - Stop all: docker-compose -f docker-compose.tier-a.yml down"
echo "   - Backup database: docker cp easm-backend-tier-a:/data/easm.db ./backup.db"
echo ""
