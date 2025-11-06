# EASM Platform - Local Development Setup

Running locally without Docker (much simpler!)

## Prerequisites

- **Python 3.11+** - `python3 --version`
- **Node.js 18+** - `node --version`
- **pip** - `pip --version`
- **npm** - `npm --version`

## Quick Start

### Option 1: Automatic (Recommended)

```bash
./run-local.sh
```

This will:
- Setup Python virtual environment
- Install all dependencies
- Create database with admin user + mock data
- Start backend on http://localhost:8000
- Start frontend on http://localhost:5173

### Option 2: Manual (Two Terminals)

**Terminal 1 - Backend:**
```bash
./run-backend-local.sh
```

**Terminal 2 - Frontend:**
```bash
./run-frontend-local.sh
```

---

## Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

---

## Access URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Interactive Docs**: http://localhost:8000/redoc

---

## Mock Data Included

The database is automatically populated with:
- ✅ 7 Assets (domains, IPs, URLs)
- ✅ 7 Scans (various statuses)
- ✅ 15 Vulnerabilities (different severities)

---

## Database Location

SQLite database: `./data/easm.db`

To reset the database:
```bash
rm -rf data/easm.db
./run-backend-local.sh  # Will recreate with fresh data
```

---

## Stopping Services

### If using tmux (automatic mode):
```bash
tmux kill-session -t easm
```

### If running manually:
Press `Ctrl+C` in each terminal

---

## Troubleshooting

### Backend won't start

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
```

### Frontend won't start

```bash
cd frontend
npm install
npm run dev
```

### Database errors

```bash
rm -rf data/easm.db
cd backend
source venv/bin/activate
python init_db.py
```

---

## Development Tips

- **Backend auto-reload**: Enabled with `--reload` flag
- **Frontend HMR**: Automatic hot module reload
- **Database viewer**: Use any SQLite browser on `data/easm.db`

---

## What's Different from Docker?

✅ **Faster startup** - No container building
✅ **Easier debugging** - See errors immediately
✅ **Live reload** - Code changes apply instantly
✅ **Direct file access** - Edit code, see database directly

---

## Production Deployment

For production, use Docker:
```bash
docker compose -f docker-compose.tier-a.yml up -d
```

But for development, local is better!
