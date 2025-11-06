#!/bin/bash
# Install Node.js 20 - Simple and reliable

set -e

echo "📦 Installing Node.js 20..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Running with sudo..."
    exec sudo bash "$0" "$@"
fi

# Remove any existing nodejs installations
echo "Removing old Node.js versions..."
apt-get remove -y nodejs npm 2>/dev/null || true

# Install using NodeSource
echo "Adding NodeSource repository..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -

echo "Installing Node.js..."
apt-get install -y nodejs

echo ""
echo "✅ Node.js installed!"
node --version
npm --version
