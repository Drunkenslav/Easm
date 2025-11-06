#!/bin/bash
# Install Python 3.11 - Simple and reliable

set -e

echo "🐍 Installing Python 3.11..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Running with sudo..."
    exec sudo bash "$0" "$@"
fi

# Check if already installed
if command -v python3.11 &> /dev/null; then
    echo "✅ Python 3.11 already installed!"
    python3.11 --version
    exit 0
fi

# Install dependencies
echo "Installing dependencies..."
apt-get update -qq
apt-get install -y software-properties-common

# Add Python PPA
echo "Adding Python repository..."
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update -qq

# Install Python 3.11
echo "Installing Python 3.11..."
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

echo ""
echo "✅ Python 3.11 installed!"
python3.11 --version
