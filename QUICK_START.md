# 🚀 Quick Start Commands

## Option 1: Use Start Script (Easiest!) ⭐

### PowerShell:
```powershell
.\start.ps1
```

### Command Prompt:
```cmd
start.bat
```

**This opens both servers in separate windows automatically!**

---

## Option 2: Manual Start (Two Terminals)

### Terminal 1 - Backend:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m api.main
```

### Terminal 2 - Frontend:

```powershell
cd frontend
npm start
```

---

## Option 3: One-Line Commands

### Backend (copy & paste):
```powershell
cd backend; .\venv\Scripts\Activate.ps1; python -m api.main
```

### Frontend (copy & paste):
```powershell
cd frontend; npm start
```

---

## ✅ Verify It's Working

**Backend:** http://localhost:8000/health  
**Frontend:** http://localhost:3000  
**API Docs:** http://localhost:8000/docs

---

## 🎯 Recommended: Use Start Script

Just run:
```powershell
.\start.ps1
```

Both servers will start automatically! 🎉

