# Backend-Frontend Connection Troubleshooting Guide

## Common Connection Issues and Solutions

### Issue 1: "Network error: Unable to connect to server"

**Symptoms:**
- Frontend shows "Backend server is not connected" banner
- All API calls fail with network errors
- Console shows connection refused errors

**Causes & Solutions:**

#### 1. Backend Server Not Running
**Solution:** Start the backend server

**Option A: Using the startup script (Windows)**
```bash
cd backend
start_server.bat
```

**Option B: Manual start**
```bash
cd backend

# Activate virtual environment (if using one)
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# Start the server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:** Open http://localhost:8000/health in your browser. You should see:
```json
{
  "status": "healthy",
  "environment": "development",
  "database": "connected"
}
```

#### 2. Backend Running on Different Port
**Check:** Look at the backend terminal output. It should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If it's on a different port, either:
- Change the backend port to 8000, OR
- Update frontend `.env` file:
  ```
  REACT_APP_API_URL=http://localhost:YOUR_PORT/api/v1
  ```

#### 3. Firewall Blocking Connection
**Solution:** 
- Windows: Check Windows Firewall settings
- Allow port 8000 through firewall
- Temporarily disable firewall to test

#### 4. Backend Dependencies Not Installed
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

---

### Issue 2: CORS Errors

**Symptoms:**
- Browser console shows CORS policy errors
- "Access-Control-Allow-Origin" errors
- Requests fail with 403/401 errors

**Solution:**
The backend CORS configuration has been updated to allow common frontend ports:
- Ports 3000-3003 (React default ports)
- Ports 5173-5175 (Vite default ports)

If your frontend is on a different port:
1. Check what port your frontend is running on (check terminal output)
2. Update `backend/config/config.py` to add your port:
```python
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:YOUR_PORT",  # Add your port here
    # ... other ports
]
```

Or update `backend/api/main.py` to allow all localhost ports in development.

---

### Issue 3: API Endpoint Not Found (404)

**Symptoms:**
- Specific API calls return 404
- "Endpoint not found" errors

**Solution:**
1. Check backend is running: http://localhost:8000/docs
2. Verify the API endpoint exists in the backend routes
3. Check the API base URL in frontend:
   - Open browser console
   - Look for: `API Base URL: http://localhost:8000/api/v1`
   - If different, check `.env` file or `frontend/src/services/api.js`

---

### Issue 4: Connection Timeout

**Symptoms:**
- Requests take a long time then fail
- "Request timed out" errors

**Solutions:**
1. **Backend is slow to respond:**
   - Check backend logs for errors
   - Restart backend server
   - Check database connection

2. **Network issues:**
   - Check internet connection
   - Try accessing http://localhost:8000 directly in browser
   - Check if antivirus is blocking connections

---

## Quick Diagnostic Steps

### Step 1: Check Backend Status
```bash
# In browser, visit:
http://localhost:8000/health

# Should return:
{"status": "healthy", ...}
```

### Step 2: Check Frontend API Configuration
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for: `API Base URL: http://localhost:8000/api/v1`
4. If different, check environment variables

### Step 3: Test API Connection
Open browser console and run:
```javascript
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

### Step 4: Check Ports
```bash
# Windows: Check if port 8000 is in use
netstat -ano | findstr :8000

# If something is using it, either:
# - Stop that process, OR
# - Change backend port in config.py
```

---

## Environment Variables

### Frontend (.env file in frontend directory)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
# OR
REACT_APP_API_BASE=http://localhost:8000
```

### Backend (.env file in backend directory)
```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ENVIRONMENT=development
DEBUG=True
```

---

## Common Ports

- **Frontend (React):** Usually 3000, 3001, 3002, 3003
- **Frontend (Vite):** Usually 5173, 5174, 5175
- **Backend:** 8000 (default)

---

## Still Having Issues?

1. **Check Backend Logs:**
   - Look at terminal where backend is running
   - Check `backend/logs/app.log` file

2. **Check Frontend Console:**
   - Open browser DevTools (F12)
   - Check Console and Network tabs
   - Look for error messages

3. **Verify Both Servers:**
   - Backend: http://localhost:8000/docs (should show API docs)
   - Frontend: http://localhost:3002 (or your frontend port)

4. **Restart Everything:**
   - Stop both frontend and backend
   - Clear browser cache
   - Restart both servers
   - Try again

---

## Testing the Connection

Once both servers are running, the Dashboard should show:
- ✅ "Backend Connected" status in header
- No red error banner at top
- API calls should work

If you see the red banner, follow the instructions in the banner to start the backend server.

