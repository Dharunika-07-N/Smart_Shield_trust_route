# 🚀 Run Commands for Smart Shield

## Quick Start Commands

### Terminal 1: Start Backend

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start FastAPI server
python -m api.main
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Backend will be available at:** http://localhost:8000

---

### Terminal 2: Start Frontend

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start React development server
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view smart-shield-frontend in the browser.

  Local:            http://localhost:3000
```

**Frontend will be available at:** http://localhost:3000

---

## 🧪 Verify Everything Works

### Test Backend Health

```powershell
# In a new terminal or browser
curl http://localhost:8000/health
```

**Or open in browser:**
```
http://localhost:8000/health
```

### Test API Docs

Open in browser:
```
http://localhost:8000/docs
```

### Test Frontend Connection

1. Open http://localhost:3000
2. Click "API Test" tab
3. Click "Test Health Check" button
4. Should see: ✅ Success!

---

## 📝 Complete Setup (First Time)

### Step 1: Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file (if not exists)
# Copy .env.example to .env and edit with your settings

# Start server
python -m api.main
```

### Step 2: Frontend Setup

```powershell
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Create .env file
@"
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_MAPBOX_TOKEN=your_token_here
"@ | Out-File -FilePath .env -Encoding utf8

# Start development server
npm start
```

---

## 🔧 Troubleshooting Commands

### Check if Backend is Running

```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Or test with curl
curl http://localhost:8000/health
```

### Check if Frontend is Running

```powershell
# Check if port 3000 is in use
netstat -ano | findstr :3000
```

### Kill Process on Port (if needed)

```powershell
# Find process ID
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Reinstall Dependencies

**Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
rm -r node_modules
rm package-lock.json
npm install
```

---

## 📋 One-Line Commands (Copy & Paste)

### Start Backend
```powershell
cd backend; .\venv\Scripts\Activate.ps1; python -m api.main
```

### Start Frontend
```powershell
cd frontend; npm start
```

### Test Backend
```powershell
curl http://localhost:8000/health
```

---

## 🎯 All-in-One Script (Windows)

Create `start.ps1` in project root:

```powershell
# Start Backend
Write-Host "Starting Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python -m api.main"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host "Both servers starting!" -ForegroundColor Yellow
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
```

Run with:
```powershell
.\start.ps1
```

---

## ✅ Success Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Health check returns: `{"status":"healthy",...}`
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Frontend loads dashboard
- [ ] API Test tab shows success

---

## 🔗 Quick Links

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Frontend:** http://localhost:3000
- **Dashboard:** http://localhost:3000/dashboard

---

**Ready to run!** 🚀

