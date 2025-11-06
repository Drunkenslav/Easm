#!/bin/bash
# Setup and run frontend locally (no Docker)

set -e

echo "🚀 Setting up Frontend - Local Development"
echo "=========================================="
echo ""

# Check Node.js
echo "1️⃣  Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
node --version
npm --version

echo ""

# Setup frontend
echo "2️⃣  Setting up frontend..."
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js dependencies..."
    npm install
fi

# Set environment variables
export PUBLIC_API_URL="http://localhost:8000/api/v1"

echo ""
echo "3️⃣  Starting frontend on http://localhost:5173 ..."
echo "   (Press Ctrl+C to stop)"
echo ""

# Start frontend
npm run dev
