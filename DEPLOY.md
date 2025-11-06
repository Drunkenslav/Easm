# 🚀 EASM Platform - Quick Deploy Guide

## One-Command Deployment

Deploy and run the EASM platform with a single command:

```bash
git clone <your-repo-url>
cd Easm
chmod +x deploy-and-run.sh
./deploy-and-run.sh
```

## What the script does:

1. **Pulls latest code** from branch `claude/lets-brain-011CUoXiygRYwFK3mMTEKvup`
2. **Sets up Python backend**:
   - Creates virtual environment
   - Installs all dependencies
   - Creates .env configuration
   - Initializes database with admin user and mock data
3. **Sets up Node.js frontend**:
   - Installs npm dependencies
4. **Starts both services**:
   - Backend API on port 8000
   - Frontend UI on port 5173

## Prerequisites

- **Python 3.9+** installed
- **Node.js 18+** and npm installed
- **Git** installed
- **(Optional) tmux** for better process management

## After Running

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

### Mock Data Included

- 7 Assets (domains, IPs, URLs)
- 7 Scans (various statuses)
- 15 Vulnerabilities
- 2 Scan Templates

## Managing Services

### If using tmux (recommended):

```bash
# View running services
tmux attach -t easm

# Switch between backend (window 0) and frontend (window 1)
Ctrl+B then 0  # Backend
Ctrl+B then 1  # Frontend

# Detach from session (services keep running)
Ctrl+B then D

# Stop all services
tmux kill-session -t easm
```

### If not using tmux:

Services will run in background. Check logs:

```bash
tail -f logs/backend.log
tail -f logs/frontend.log
```

Stop services by killing the PIDs shown in the output.

## Manual Setup (Alternative)

If you prefer to set up manually:

### Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Environment Configuration

The script creates a default `.env` file in the backend directory. To customize:

```bash
# backend/.env
DATABASE_URL=sqlite:///./data/easm.db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
APP_TIER=A
DEBUG=true
```

## Troubleshooting

### Port already in use:
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :5173

# Kill the processes if needed
kill -9 <PID>
```

### Python version issues:
```bash
# Use specific Python version
python3.11 -m venv venv
```

### Node.js version issues:
```bash
# Use nvm to switch versions
nvm install 20
nvm use 20
```

## Production Deployment

For production, use Docker Compose:

```bash
docker compose -f docker-compose.yml up -d
```

See `docker-compose.tier-*.yml` for different deployment tiers.
