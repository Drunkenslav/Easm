#!/bin/bash
# Install Docker Engine and Docker Compose V2 on Ubuntu
# Run with: sudo ./install-docker.sh

set -e

echo "🐳 Installing Docker Engine on Ubuntu..."
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo ./install-docker.sh"
    exit 1
fi

# Update package index
echo "📦 Updating package index..."
apt-get update

# Install prerequisites
echo "📦 Installing prerequisites..."
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
echo "🔑 Adding Docker GPG key..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo "📦 Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
apt-get update

# Install Docker Engine
echo "🐳 Installing Docker Engine..."
apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Start and enable Docker service
echo "🚀 Starting Docker service..."
systemctl start docker
systemctl enable docker

# Add current user to docker group (if not root)
if [ -n "$SUDO_USER" ]; then
    echo "👤 Adding user '$SUDO_USER' to docker group..."
    usermod -aG docker $SUDO_USER
    echo "⚠️  Note: User needs to logout and login again for group changes to take effect"
fi

# Verify installation
echo ""
echo "✅ Docker installation complete!"
echo ""
echo "📊 Docker version:"
docker version

echo ""
echo "📊 Docker Compose version:"
docker compose version

echo ""
echo "✅ Installation successful!"
echo ""
echo "🔄 Next steps:"
echo "   1. Logout and login again (or run: newgrp docker)"
echo "   2. Test Docker: docker run hello-world"
echo "   3. Deploy EASM: ./deploy-tier-a.sh"
echo ""
