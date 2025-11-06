#!/bin/bash
set -e

echo "🚀 EASM Platform - Deploy and Run Script"
echo "========================================"
echo ""

# Configuration
BRANCH="claude/lets-brain-011CUoXiygRYwFK3mMTEKvup"
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}📥 Step 1: Pulling latest code...${NC}"
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH
echo -e "${GREEN}✅ Code updated${NC}"
echo ""

echo -e "${BLUE}🐍 Step 2: Setting up Python backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cat > .env << 'ENVEOF'
DATABASE_URL=sqlite:///./data/easm.db
SECRET_KEY=dev-secret-key-local-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-local-change-in-production
APP_TIER=A
DEBUG=true
ENVEOF
fi

# Create data directory
mkdir -p data

# Initialize database
echo "Initializing database with admin user and mock data..."
python init_db.py

echo -e "${GREEN}✅ Backend setup complete${NC}"
echo ""

echo -e "${BLUE}📦 Step 3: Setting up Node.js frontend...${NC}"
cd ../frontend

# Install npm dependencies
echo "Installing Node.js dependencies..."
npm install --silent

echo -e "${GREEN}✅ Frontend setup complete${NC}"
echo ""

echo -e "${BLUE}🎯 Step 4: Starting services...${NC}"
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}⚠️  tmux not found. Installing services without tmux...${NC}"
    echo ""
    echo "Starting backend in background..."
    cd "$SCRIPT_DIR/backend"
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"

    echo "Starting frontend in background..."
    cd "$SCRIPT_DIR/frontend"
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"

    echo ""
    echo -e "${GREEN}✅ Services started!${NC}"
    echo ""
    echo "Backend PID: $BACKEND_PID (log: logs/backend.log)"
    echo "Frontend PID: $FRONTEND_PID (log: logs/frontend.log)"
    echo ""
    echo "To view logs:"
    echo "  Backend:  tail -f logs/backend.log"
    echo "  Frontend: tail -f logs/frontend.log"
    echo ""
    echo "To stop services:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
else
    # Use tmux for better management
    TMUX_SESSION="easm"

    # Kill existing session if it exists
    tmux kill-session -t $TMUX_SESSION 2>/dev/null || true

    # Create new tmux session
    echo "Creating tmux session '$TMUX_SESSION'..."

    # Start backend in first window
    tmux new-session -d -s $TMUX_SESSION -n backend
    tmux send-keys -t $TMUX_SESSION:backend "cd $SCRIPT_DIR/backend" C-m
    tmux send-keys -t $TMUX_SESSION:backend "source venv/bin/activate" C-m
    tmux send-keys -t $TMUX_SESSION:backend "uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload" C-m

    # Start frontend in second window
    tmux new-window -t $TMUX_SESSION -n frontend
    tmux send-keys -t $TMUX_SESSION:frontend "cd $SCRIPT_DIR/frontend" C-m
    tmux send-keys -t $TMUX_SESSION:frontend "npm run dev" C-m

    # Select backend window
    tmux select-window -t $TMUX_SESSION:backend

    echo -e "${GREEN}✅ Services started in tmux session!${NC}"
    echo ""
    echo "Tmux session: $TMUX_SESSION"
    echo ""
    echo "To attach to the session:"
    echo "  tmux attach -t $TMUX_SESSION"
    echo ""
    echo "To switch between windows (when attached):"
    echo "  Ctrl+B then 0 (backend)"
    echo "  Ctrl+B then 1 (frontend)"
    echo ""
    echo "To detach from session:"
    echo "  Ctrl+B then D"
    echo ""
    echo "To stop all services:"
    echo "  tmux kill-session -t $TMUX_SESSION"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 EASM Platform is running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Backend:  http://localhost:$BACKEND_PORT"
echo "   API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "🔐 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 Mock data loaded:"
echo "   - 7 Assets"
echo "   - 7 Scans"
echo "   - 15 Vulnerabilities"
echo "   - 2 Scan Templates"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
