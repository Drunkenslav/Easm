#!/bin/sh
# Startup script for backend container
# Initializes database with admin user and mock data, then starts uvicorn

set -e

echo "🚀 Starting EASM Backend..."
echo ""

# Initialize database with admin user and mock data
echo "📊 Initializing database..."
python init_db.py

echo ""
echo "🌐 Starting API server..."

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
