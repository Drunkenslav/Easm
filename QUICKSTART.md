# ⚡ EASM Platform - Quick Start (NO DOCKER)

## 🚀 One Command Setup

```bash
sudo ./setup-complete.sh
```

This installs **EVERYTHING**:
- ✅ Python 3.11
- ✅ Node.js 20
- ✅ All system packages (build tools, SQLite, etc.)
- ✅ All Python packages (FastAPI, SQLAlchemy, etc.)
- ✅ All Node.js packages (SvelteKit, Vite, etc.)
- ✅ Nuclei vulnerability scanner
- ✅ tmux

**Takes ~3-5 minutes depending on internet speed.**

---

## 🏃 Run the Platform

After setup completes:

```bash
./run-local.sh
```

**That's it!** Wait 30 seconds, then go to:

👉 **http://localhost:5173**

Login:
- **Username**: `admin`
- **Password**: `admin123`

---

## 📊 What You'll See

- ✅ **7 Assets** (example.com, api.example.com, etc.)
- ✅ **15 Vulnerabilities** (SQL Injection, XSS, RCE, etc.)
- ✅ **7 Scans** (completed, running, failed)
- ✅ **Full dashboard** with charts and stats

---

## 🛑 Stop Everything

```bash
tmux kill-session -t easm
```

Or press `Ctrl+C` in each terminal if running manually.

---

## 🔧 Manual Control (Optional)

If you prefer separate terminals:

**Terminal 1 - Backend:**
```bash
./run-backend-local.sh
```

**Terminal 2 - Frontend:**
```bash
./run-frontend-local.sh
```

---

## 📝 What Each Script Does

### `setup-complete.sh`
- Installs system dependencies (Python, Node.js, etc.)
- Creates Python virtual environment
- Installs all Python packages
- Installs all Node.js packages
- **Run once with sudo**

### `run-backend-local.sh`
- Activates Python venv
- Creates database with admin user + mock data
- Starts FastAPI on port 8000

### `run-frontend-local.sh`
- Starts SvelteKit dev server on port 5173
- Hot reload enabled

### `run-local.sh`
- Runs both backend and frontend together
- Uses tmux for convenience

---

## 🐛 Troubleshooting

### "sudo: ./setup-complete.sh: command not found"
```bash
chmod +x setup-complete.sh
sudo ./setup-complete.sh
```

### "Python packages failed to install"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Cannot find module '@sveltejs/kit'"
```bash
cd frontend
npm install
```

### Reset everything
```bash
rm -rf backend/venv frontend/node_modules data/
sudo ./setup-complete.sh
./run-local.sh
```

---

## 🎯 URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |

---

## 💾 Database

Location: `./data/easm.db` (SQLite)

View with any SQLite browser:
```bash
sqlite3 data/easm.db
.tables
SELECT * FROM users;
```

---

## ⚠️ Ubuntu Only

This script is for **Ubuntu/Debian**. For other OS:

**macOS:**
- Install Python 3.11: `brew install python@3.11`
- Install Node.js: `brew install node@20`
- Then run backend/frontend scripts manually

**Windows:**
- Install Python 3.11 from python.org
- Install Node.js from nodejs.org
- Use PowerShell to run scripts

---

## 🎉 That's It!

Two commands:
1. `sudo ./setup-complete.sh` (once)
2. `./run-local.sh` (every time you want to start)

**No Docker, no hassle!** 🚀
