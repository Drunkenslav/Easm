#!/bin/sh
# Startup script for backend container
# Initializes database with admin user and mock data, then starts uvicorn

echo "🚀 Starting EASM Backend..."
echo ""

# Initialize database with admin user and mock data
echo "📊 Initializing database..."
python init_db.py || {
    echo "⚠️  Database initialization had issues, but continuing..."
    echo "   You may need to run /api/v1/auth/init manually"
}

echo ""
echo "🌐 Starting API server..."

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
