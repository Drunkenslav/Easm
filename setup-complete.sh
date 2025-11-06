#!/bin/bash
# Complete EASM Platform Setup - Installs EVERYTHING needed

set -e

echo "🚀 EASM Platform - Complete Setup"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script needs sudo privileges to install system packages"
    echo "   Re-running with sudo..."
    exec sudo bash "$0" "$@"
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo "Installing for user: $ACTUAL_USER"
echo "Home directory: $ACTUAL_HOME"
echo ""

# Update package lists
echo "1️⃣  Updating package lists..."
apt-get update -qq

echo ""

# Install Python 3.11
echo "2️⃣  Installing Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    apt-get install -y software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -qq
    apt-get install -y python3.11 python3.11-venv python3.11-dev
    # Set python3 to point to python3.11
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
fi
python3 --version

echo ""

# Install pip
echo "3️⃣  Installing pip..."
if ! command -v pip3 &> /dev/null; then
    apt-get install -y python3-pip
fi
pip3 --version

echo ""

# Install Node.js 20
echo "4️⃣  Installing Node.js 20..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
node --version
npm --version

echo ""

# Install system dependencies for Python packages
echo "5️⃣  Installing system dependencies..."
apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    sqlite3 \
    curl \
    wget \
    git \
    tmux

echo ""

# Install Nuclei (optional, for vulnerability scanning)
echo "6️⃣  Installing Nuclei scanner..."
if ! command -v nuclei &> /dev/null; then
    wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip
    unzip -q nuclei_linux_amd64.zip
    mv nuclei /usr/local/bin/nuclei
    chmod +x /usr/local/bin/nuclei
    rm nuclei_linux_amd64.zip
    nuclei -update-templates > /dev/null 2>&1 || true
fi
nuclei -version 2>/dev/null || echo "Nuclei installed (version check skipped)"

echo ""
echo "=================================="
echo "✅ System dependencies installed!"
echo ""

# Now setup the application as the actual user
echo "7️⃣  Setting up application..."
cd "$ACTUAL_HOME/Easm" || cd /home/user/Easm || cd "$(dirname "$0")"

# Backend setup
echo ""
echo "   Setting up backend..."
cd backend

# Create virtual environment as actual user
if [ ! -d "venv" ]; then
    echo "   Creating Python virtual environment..."
    sudo -u $ACTUAL_USER python3 -m venv venv
fi

# Activate and install Python packages
echo "   Installing Python packages..."
sudo -u $ACTUAL_USER bash << 'EOF'
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "   ✅ Python packages installed"
EOF

# Frontend setup
echo ""
echo "   Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js packages..."
    sudo -u $ACTUAL_USER npm install --silent
    echo "   ✅ Node.js packages installed"
else
    echo "   ✅ Node.js packages already installed"
fi

# Create data directory
cd ..
mkdir -p data
chown $ACTUAL_USER:$ACTUAL_USER data

echo ""
echo "=================================="
echo "✅ COMPLETE SETUP FINISHED!"
echo ""
echo "📦 Installed:"
echo "   - Python $(python3 --version | cut -d' ' -f2)"
echo "   - Node.js $(node --version)"
echo "   - npm $(npm --version)"
echo "   - All Python packages (FastAPI, SQLAlchemy, etc.)"
echo "   - All Node.js packages (SvelteKit, Vite, etc.)"
echo "   - Nuclei scanner"
echo "   - SQLite"
echo "   - tmux"
echo ""
echo "🚀 Ready to run!"
echo ""
echo "Run as user $ACTUAL_USER:"
echo "   ./run-local.sh"
echo ""
echo "Or manually:"
echo "   Terminal 1: ./run-backend-local.sh"
echo "   Terminal 2: ./run-frontend-local.sh"
echo ""
