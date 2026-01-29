# Quick Start Guide - SmartShield Dashboard

## Getting Started

### 1. Start the Application

The application should already be running. If not, use:

```bash
# Backend (from project root)
cd backend && venv\Scripts\activate && python -m api.main

# Frontend (from project root)
cd frontend && npm start
```

### 2. Access the Dashboard

1. Open your browser to: **http://localhost:3000**
2. You'll see the login page
3. Click the **"Skip Login (Dev)"** button in the top-right corner
4. You'll be redirected to the Modern Dashboard

## Dashboard Features

### Main Dashboard View

When you first load the dashboard, you'll see:

#### 📊 **Stats Grid** (Top Section)
- **Active Deliveries**: Shows current delivery count with trend
- **Safety Score**: Overall safety percentage
- **Fuel Saved**: Weekly fuel savings in liters
- **Avg. Delivery Time**: Average time per delivery

#### 🗺️ **Active Route Map** (Center-Left)
- Light-themed interactive map
- Shows current route with safety scores
- Zoom controls and layer options
- Route score badge (e.g., "Route 78")

#### 📦 **Delivery Queue** (Below Map)
- List of active deliveries
- Each delivery shows:
  - Customer name and address
  - Estimated time and distance
  - Safety score (large green number)
  - Priority badge (High/Normal/Urgent)
  - Status (In Transit/Pending/Scheduled)

#### ⚡ **Quick Actions** (Right Panel - Top)
- **Optimize Route** (Green button) - Click to optimize current route
- **Find Safe Zone** - Locate nearest safe area
- **Report Issue** - Submit safety concerns
- **Emergency** (Orange button) - Quick dial emergency

#### 🛡️ **Zone Safety** (Right Panel - Middle)
- Shows safety scores for different zones
- Incident counts with trend arrows
- Progress bars showing safety levels
- Color-coded: Green (safe), Amber (caution), Red (danger)

#### ☁️ **Weather Conditions** (Right Panel - Bottom)
- Current temperature and weather icon
- Humidity percentage
- Wind speed
- Visibility status
- Impact level on deliveries

## Using Key Features

### Optimize Route
1. Click the green **"Optimize Route"** button in Quick Actions
2. An alert will show:
   - Optimization status
   - Estimated time saved
   - Fuel saved
3. The route will be recalculated based on current deliveries

### View Delivery Details
- Each delivery card in the queue shows:
  - **ID**: Delivery reference number
  - **Priority**: Color-coded badge
  - **Status**: Current delivery state
  - **Safety Score**: Large number (0-100)
  - **Customer Info**: Name and full address
  - **Metrics**: Time and distance estimates

### Monitor Zone Safety
- The Zone Safety panel updates in real-time
- Look for:
  - **Green zones** (88-100): Very safe
  - **Amber zones** (60-87): Moderate safety
  - **Red zones** (0-59): High risk
- Trend arrows show if safety is improving (↓) or declining (↑)

### Check Weather Impact
- Weather panel shows current conditions
- Impact badge indicates effect on deliveries:
  - **Low Impact**: Normal operations
  - **Medium Impact**: Minor delays possible
  - **High Impact**: Significant delays expected

## Navigation

### Sidebar Menu
Click any menu item to navigate:
- **Dashboard** - Main overview (current view)
- **Route Map** - Full-screen map view
- **Deliveries** - Complete delivery list
- **Safety Zones** - Zone management
- **Alerts** - Safety alerts and notifications
- **Analytics** - Performance metrics
- **Fuel Metrics** - Fuel consumption data
- **Feedback** - Submit feedback
- **Settings** - User preferences

### Collapse Sidebar
- Click the menu icon (☰) in the header to collapse/expand the sidebar
- Collapsed view shows only icons

## Data Refresh

- **Automatic**: Dashboard data refreshes every 30 seconds
- **Manual**: Refresh your browser to force update
- **Loading States**: Spinning indicators show when data is loading

## API Endpoints Being Used

The dashboard connects to these backend endpoints:

1. **GET** `/api/v1/dashboard/stats` - Dashboard statistics
2. **GET** `/api/v1/dashboard/deliveries/queue` - Delivery queue
3. **GET** `/api/v1/dashboard/zones/safety` - Zone safety data
4. **GET** `/api/v1/dashboard/weather` - Weather conditions
5. **POST** `/api/v1/dashboard/route/optimize` - Route optimization

## Troubleshooting

### Dashboard Not Loading
- Check that both backend (port 8000) and frontend (port 3000) are running
- Open browser console (F12) to check for errors
- Verify API_BASE_URL in `frontend/src/utils/constants.js`

### No Data Showing
- Look for loading spinners - data may still be fetching
- Check browser console for API errors
- Verify backend is running: http://localhost:8000/health

### Map Not Displaying
- Ensure internet connection (map tiles load from external source)
- Check browser console for Leaflet errors
- Try refreshing the page

### Optimize Route Not Working
- Ensure you have active deliveries in the queue
- Check browser console for error messages
- Verify backend is responding: http://localhost:8000/api/v1/dashboard/stats

## Development Features

### Dev Login Bypass
- The "Skip Login (Dev)" button is for development only
- It sets a mock auth token in localStorage
- Remove this button before production deployment

### Mock Data
- If API calls fail, the dashboard falls back to default mock data
- This ensures the UI remains functional during development

## Next Steps

1. **Explore the Dashboard**: Click around and familiarize yourself with the layout
2. **Test Route Optimization**: Click "Optimize Route" to see it in action
3. **Monitor Real-time Updates**: Watch the data refresh every 30 seconds
4. **Check Different Zones**: Review safety scores across different areas
5. **View Weather Impact**: See how weather affects delivery operations

## Additional Resources

- **Full Feature Documentation**: See `FEATURES_IMPLEMENTED.md`
- **API Documentation**: Visit http://localhost:8000/docs (Swagger UI)
- **Project README**: See `README.md` for complete project overview

## Support

For issues or questions:
1. Check browser console for errors
2. Review backend logs in the terminal
3. Verify all dependencies are installed
4. Ensure both servers are running

---

**Enjoy your SmartShield Dashboard!** 🚀
