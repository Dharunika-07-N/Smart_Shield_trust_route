# 🚀 Quick Run Commands

## Option 1: Quick Start (Automated) ⚡

### Windows PowerShell:
```powershell
.\start.ps1
```

### Windows Command Prompt:
```cmd
start.bat
```

This will automatically start both backend and frontend in separate windows.

---

## Option 2: Manual Start (Two Terminals) 🔧

### Terminal 1: Start Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m api.main
```

**Backend will run on:** http://localhost:8000

---

### Terminal 2: Start Frontend

```powershell
cd frontend
npm start
```

**Frontend will run on:** http://localhost:3000

---

## Option 3: One-Line Commands (Copy & Paste) 📋

### Backend (PowerShell):
```powershell
cd backend; .\venv\Scripts\Activate.ps1; python -m api.main
```

### Frontend (PowerShell):
```powershell
cd frontend; npm start
```

---

## ✅ Verify Everything Works

### 1. Check Backend Health:
Open in browser: http://localhost:8000/health

Or in terminal:
```powershell
curl http://localhost:8000/health
```

### 2. Check API Documentation:
Open in browser: http://localhost:8000/docs

### 3. Open Frontend Dashboard:
Open in browser: http://localhost:3000

---

## 📍 Important URLs

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend App**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard

---

## 🔧 First Time Setup (If Needed)

### Backend Setup:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Setup:
```powershell
cd frontend
npm install
```

---

## ⚠️ Troubleshooting

### Backend won't start?
- Check if port 8000 is already in use: `netstat -ano | findstr :8000`
- Make sure virtual environment is activated
- Check if all dependencies are installed: `pip list`

### Frontend won't start?
- Check if port 3000 is already in use: `netstat -ano | findstr :3000`
- Make sure node_modules are installed: `npm install`
- Clear cache: `npm start -- --reset-cache`

### Kill a process on a port:
```powershell
# Find the process ID
netstat -ano | findstr :8000

# Kill it (replace PID with the number from above)
taskkill /PID <PID> /F
```

---

## 🎯 Recommended: Use the Start Scripts

**Easiest way:** Just run:
```powershell
.\start.ps1
```

This automatically:
- ✅ Starts backend in a new window
- ✅ Waits 5 seconds for backend to initialize
- ✅ Starts frontend in a new window
- ✅ Shows you all the URLs

---

**Ready to go!** 🚀


