# Install Step-by-Step (Copy-Paste Each Command)

Just copy and paste these commands **ONE BY ONE**. Don't run scripts.

---

## 1. Install Node.js 20

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version
```

---

## 2. Install Python 3.11

```bash
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
python3.11 --version
```

---

## 3. Install System Packages

```bash
sudo apt-get install -y build-essential libssl-dev libffi-dev sqlite3 curl wget git tmux
```

---

## 4. Setup Backend

```bash
cd ~/Easm/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Setup Frontend

```bash
cd ~/Easm/frontend
npm install
```

---

## 6. Create Database

```bash
cd ~/Easm
mkdir -p data
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite+aiosqlite:///../data/easm.db"
python init_db.py
```

---

## 7. Run Backend (Terminal 1)

```bash
cd ~/Easm/backend
source venv/bin/activate
export DATABASE_URL="sqlite+aiosqlite:///../data/easm.db"
export SECRET_KEY="dev-secret"
export JWT_SECRET_KEY="dev-jwt-secret"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Keep this terminal open!

---

## 8. Run Frontend (Terminal 2 - Open New Terminal)

```bash
cd ~/Easm/frontend
npm run dev
```

Keep this terminal open!

---

## 9. Open Browser

Go to: **http://localhost:5173**

Login:
- Username: **admin**
- Password: **admin123**

---

## Done! 🎉

Both terminals must stay open. Press Ctrl+C in each terminal to stop.
