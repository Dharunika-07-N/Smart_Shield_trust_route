# Troubleshooting Guide

## Issue: "Cannot connect to server" Error

### Step 1: Verify Backend is Running

Open a new terminal and run:

```bash
cd backend
python -m uvicorn api.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Test Backend Connection

Open a new terminal and test the backend:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy",...}
```

Or open in browser: http://localhost:8000/health

### Step 3: Check Frontend API Configuration

1. Open browser console (F12)
2. Look for: `API Base URL: http://localhost:8000/api/v1`
3. If you see `/api/v1` instead, there's an environment variable override

### Step 4: Fix API URL (if needed)

If the API is using `/api/v1` instead of `http://localhost:8000/api/v1`:

**Option A: Set environment variable**
Create a `.env` file in the `frontend` folder:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

**Option B: Remove proxy (if causing issues)**
The `package.json` has a proxy set. If it's not working, you can:
1. Remove the `"proxy": "http://localhost:8000"` line from `frontend/package.json`
2. Restart the React dev server

### Step 5: Restart Both Servers

1. **Stop** both frontend and backend servers (Ctrl+C)
2. **Start backend first:**
   ```bash
   cd backend
   python -m uvicorn api.main:app --reload
   ```
3. **Then start frontend** (in a new terminal):
   ```bash
   cd frontend
   npm start
   ```

### Step 6: Verify Connection

1. Open browser console (F12)
2. Go to Network tab
3. Try to optimize a route
4. Look for requests to `http://localhost:8000/api/v1/delivery/optimize`
5. Check if they're successful (200) or failing (CORS, connection refused, etc.)

### Common Issues

#### Issue: CORS Error
**Solution:** Backend CORS is already configured. Make sure backend is running on port 8000.

#### Issue: Connection Refused
**Solution:** Backend server is not running. Start it with Step 1.

#### Issue: 404 Not Found
**Solution:** Check that the endpoint path is correct: `/api/v1/delivery/optimize`

#### Issue: Environment Variable Not Working
**Solution:** 
- React requires environment variables to start with `REACT_APP_`
- After changing `.env`, restart the React dev server
- Clear browser cache if needed

### Quick Test Commands

```bash
# Test backend health
curl http://localhost:8000/health

# Test route optimization (replace coordinates with your values)
curl -X POST http://localhost:8000/api/v1/delivery/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "starting_point": {"latitude": 10.9894, "longitude": 76.9598},
    "stops": [{
      "stop_id": "DEST_1",
      "address": "Destination",
      "coordinates": {"latitude": 10.9669, "longitude": 76.9543},
      "priority": "high"
    }],
    "optimize_for": ["time", "distance"]
  }'
```

If the curl command works but the frontend doesn't, it's a frontend configuration issue.
