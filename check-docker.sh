#!/bin/bash
# Check Docker installation and diagnose common issues

echo "🔍 Docker Diagnostics"
echo "===================="
echo ""

# Check if Docker is installed
echo "1️⃣  Checking if Docker is installed..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker CLI found: $(which docker)"
    docker --version
else
    echo "   ❌ Docker is NOT installed"
    echo "   📝 To install: sudo ./install-docker.sh"
    exit 1
fi

echo ""

# Check if Docker daemon is running
echo "2️⃣  Checking if Docker daemon is running..."
if docker info &> /dev/null; then
    echo "   ✅ Docker daemon is running"
else
    echo "   ❌ Cannot connect to Docker daemon"
    echo ""
    echo "   Possible causes:"
    echo "   1. Docker service is not started"
    echo "      Fix: sudo systemctl start docker"
    echo ""
    echo "   2. User doesn't have permission"
    echo "      Fix: sudo usermod -aG docker $USER"
    echo "      Then: logout and login again"
    echo ""
    echo "   3. Docker socket permissions"
    echo "      Fix: sudo chmod 666 /var/run/docker.sock"
    echo ""
    exit 1
fi

echo ""

# Check Docker service status
echo "3️⃣  Checking Docker service status..."
if systemctl is-active --quiet docker; then
    echo "   ✅ Docker service is active"
else
    echo "   ⚠️  Docker service is not active"
    echo "   Fix: sudo systemctl start docker"
fi

echo ""

# Check user groups
echo "4️⃣  Checking user groups..."
if groups | grep -q docker; then
    echo "   ✅ User '$USER' is in docker group"
else
    echo "   ⚠️  User '$USER' is NOT in docker group"
    echo "   Fix: sudo usermod -aG docker $USER"
    echo "   Then: logout and login again"
fi

echo ""

# Check Docker Compose
echo "5️⃣  Checking Docker Compose..."
if docker compose version &> /dev/null; then
    echo "   ✅ Docker Compose found"
    docker compose version
else
    echo "   ❌ Docker Compose NOT found"
    echo "   Fix: Install docker-compose-plugin"
fi

echo ""

# Test Docker
echo "6️⃣  Testing Docker functionality..."
if docker ps &> /dev/null; then
    echo "   ✅ Docker is working!"
    echo ""
    echo "   📊 Running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo "   ❌ Docker test failed"
fi

echo ""
echo "===================="
echo "✅ Diagnostics complete!"
echo ""
