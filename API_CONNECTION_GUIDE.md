# 🔌 API Connection Guide

## Frontend-Backend Connection Setup

Complete guide for connecting frontend React app to FastAPI backend.

---

## ✅ What's Been Fixed

### 1. **API Client Service** (`frontend/src/services/api.js`)
- ✅ Axios-based API client
- ✅ Automatic base URL configuration
- ✅ Request/response interceptors
- ✅ Error handling
- ✅ Auth token support

### 2. **CORS Configuration** (Backend)
- ✅ Enhanced CORS middleware
- ✅ Supports multiple frontend ports (3000, 5173-5175)
- ✅ Allows all necessary HTTP methods
- ✅ Proper headers exposed

### 3. **Environment Configuration**
- ✅ `.env` file for frontend
- ✅ API URL configuration
- ✅ Proxy fallback in package.json

### 4. **API Test Component**
- ✅ Connection testing UI
- ✅ Health check endpoint test
- ✅ Route optimization test
- ✅ Troubleshooting tips

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

python -m api.main
```

Backend should run on: **http://localhost:8000**

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend should run on: **http://localhost:3000**

### 3. Test Connection

1. Open frontend: http://localhost:3000
2. Navigate to **"API Test"** tab
3. Click **"Test Health Check"** button
4. You should see: ✅ Backend connection successful!

---

## 📁 Configuration Files

### Frontend `.env`

Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_MAPBOX_TOKEN=your_token_here
```

### Backend CORS

Already configured in `backend/config/config.py`:
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]
```

### Package.json Proxy

In `frontend/package.json`:
```json
{
  "proxy": "http://localhost:8000"
}
```

---

## 🔧 Using the API Client

### Basic Usage

```javascript
import { api } from '../services/api';

// Health check
const health = await api.healthCheck();

// Optimize route
const route = await api.optimizeRoute({
  starting_point: { latitude: 40.7128, longitude: -74.0060 },
  stops: [...],
  optimize_for: ['time', 'safety']
});

// Get traffic data
const traffic = await api.getTrafficRoute({
  coordinates: [...]
});
```

### Using Hooks

```javascript
import { useRouteOptimization, useTrafficData } from '../hooks/useApi';

function MyComponent() {
  const { result, loading, error, optimize } = useRouteOptimization();
  const { trafficData, getTrafficForRoute } = useTrafficData();

  const handleOptimize = async () => {
    try {
      await optimize(routeData);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {result && <p>Success!</p>}
    </div>
  );
}
```

---

## 🧪 Testing API Connection

### Method 1: Using API Test Component

1. Navigate to "API Test" tab in dashboard
2. Click test buttons
3. View results and troubleshooting tips

### Method 2: Browser Console

```javascript
// Open browser console (F12)
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

### Method 3: curl

```bash
# Health check
curl http://localhost:8000/health

# Test with data
curl -X POST http://localhost:8000/api/v1/delivery/optimize \
  -H "Content-Type: application/json" \
  -d '{"starting_point":{"latitude":40.7128,"longitude":-74.0060},"stops":[],"optimize_for":["time"]}'
```

---

## 🐛 Troubleshooting

### Issue: CORS Error

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/api/v1/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Solution:**
1. Check backend CORS settings in `backend/config/config.py`
2. Make sure frontend URL is in `BACKEND_CORS_ORIGINS`
3. Restart backend server

### Issue: Network Error

**Symptoms:**
```
Network error: Unable to connect to server
```

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check backend port (should be 8000)
3. Check firewall settings
4. Verify `.env` file has correct `REACT_APP_API_URL`

### Issue: 404 Not Found

**Symptoms:**
```
404 Not Found
```

**Solution:**
1. Check API endpoint path (should start with `/api/v1`)
2. Verify backend routes are registered
3. Check API docs: http://localhost:8000/docs

### Issue: Proxy Not Working

**Symptoms:**
Frontend can't reach backend via proxy

**Solution:**
1. Use explicit URL in `.env`: `REACT_APP_API_URL=http://localhost:8000/api/v1`
2. Restart frontend dev server after changing `.env`
3. Clear browser cache

---

## 📋 API Endpoints Reference

### Health
- `GET /health` - Health check

### Delivery
- `POST /api/v1/delivery/optimize` - Optimize route
- `GET /api/v1/delivery/routes/{id}` - Get route
- `PUT /api/v1/delivery/routes/{id}` - Update route
- `GET /api/v1/delivery/stats` - Delivery stats

### Safety
- `POST /api/v1/safety/score` - Calculate safety score
- `POST /api/v1/safety/heatmap` - Get heatmap
- `POST /api/v1/safety/conditions/{location}` - Get conditions

### Feedback
- `POST /api/v1/feedback/submit` - Submit feedback
- `GET /api/v1/feedback/stats` - Feedback stats

### Traffic
- `POST /api/v1/traffic/segment` - Get segment traffic
- `POST /api/v1/traffic/route` - Get route traffic

---

## 🔐 Authentication (Future)

Currently, the API is open. For production:

1. Add JWT authentication
2. Store tokens in localStorage
3. API client automatically includes token in requests
4. Backend validates tokens

---

## ✅ Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] `.env` file configured
- [ ] CORS settings correct
- [ ] API Test component shows success
- [ ] Browser console has no CORS errors
- [ ] API calls return data

---

## 🎉 Success Indicators

When everything is working:

✅ API Test shows green checkmark  
✅ No CORS errors in browser console  
✅ API calls return data  
✅ Routes load successfully  
✅ Traffic data displays  
✅ Safety scores calculate  

---

**Your frontend and backend are now connected!** 🚀

Test the connection using the "API Test" tab in the dashboard.

