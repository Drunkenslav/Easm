#!/bin/bash
# Setup and run EASM Platform locally (no Docker)

set -e

echo "🚀 Setting up EASM Platform - Local Development"
echo "==============================================="
echo ""

# Check Python
echo "1️⃣  Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.11+"
    exit 1
fi
python3 --version

echo ""

# Setup backend
echo "2️⃣  Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "   Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create data directory
mkdir -p ../data

# Set environment variable
export DATABASE_URL="sqlite+aiosqlite:///../data/easm.db"
export SECRET_KEY="dev-secret-key-change-in-production"
export JWT_SECRET_KEY="dev-jwt-secret-key-change-in-production"

# Initialize database
echo "   Initializing database with admin user and mock data..."
python init_db.py

echo ""
echo "3️⃣  Starting backend on http://localhost:8000 ..."
echo "   (Press Ctrl+C to stop)"
echo ""

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
