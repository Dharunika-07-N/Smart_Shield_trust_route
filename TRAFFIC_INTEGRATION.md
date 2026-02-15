# Traffic Data Integration

## Overview

Smart Shield now integrates **real-time traffic data** from multiple open-source providers to enhance route optimization and safety scoring. This integration uses:

- **OpenTraffic** - Community-driven real-time traffic speed data
- **OpenStreetMap** - Road network data with intelligent traffic estimation
- **Custom Algorithms** - Time-based traffic prediction when real data is unavailable

## Features

### ✅ Multi-Source Traffic Data
- **Primary**: OpenTraffic API for real-time traffic speeds
- **Fallback**: OSM-based traffic estimation using road types and time of day
- **Caching**: 5-minute cache to reduce API calls
- **Auto-refresh**: Updates every 60 seconds on the map

### ✅ Traffic Levels
| Level | Description | Speed Ratio | Color |
|-------|-------------|-------------|-------|
| 🟢 FREE_FLOW | Traffic flowing freely | ≥85% | Green |
| 🟡 LIGHT | Light traffic | 65-85% | Lime |
| 🟠 MODERATE | Moderate congestion | 45-65% | Amber |
| 🔴 HEAVY | Heavy traffic | 25-45% | Orange |
| 🚨 SEVERE | Severe congestion | <25% | Red |

### ✅ API Endpoints

#### Get Traffic Segments
```http
GET /api/traffic/segments?min_lat=13.0&min_lng=80.0&max_lat=13.1&max_lng=80.3
```

Returns traffic data for a bounding box with speed and congestion levels.

#### Analyze Route Traffic
```http
POST /api/traffic/route
Content-Type: application/json

{
  "coordinates": [[13.0827, 80.2707], [13.0850, 80.2750]]
}
```

Returns overall traffic level and segment analysis for a route.

#### Service Status
```http
GET /api/traffic/status
```

Shows which traffic data providers are available and operational.

#### Traffic Level Definitions
```http
GET /api/traffic/levels
```

Returns all traffic level definitions with colors and descriptions.

## Architecture

### Backend (`backend/app/services/traffic_data.py`)

```
TrafficDataAggregator
├── OpenTrafficProvider (Priority 10)
│   ├── Fetches real-time speed data
│   └── Uses OpenTraffic API
└── OSMTrafficEstimator (Priority 1)
    ├── Fallback when OpenTraffic unavailable
    ├── Fetches road data from Overpass API
    └── Estimates traffic based on:
        - Road type (motorway, primary, etc.)
        - Time of day (peak vs off-peak)
        - Typical speed patterns
```

### Frontend (`frontend/src/services/trafficApi.js`)

- **API Client**: Axios-based service for traffic endpoints
- **Utilities**: Format traffic levels, calculate delays, convert to map layers
- **Constants**: Traffic level definitions and color schemes

### Map Component (`frontend/src/components/TrafficLayer.jsx`)

- **Real-time Overlay**: Shows traffic as colored polylines on map
- **Auto-refresh**: Updates every 60 seconds
- **Interactive**: Click segments to see speed and congestion details
- **Responsive**: Fetches new data when map moves

## Usage

### 1. Backend Setup

The traffic module is automatically available. No additional setup needed!

```python
from app.services.traffic_data import get_traffic_data, get_route_traffic

# Get traffic for an area
bbox = (13.0, 80.0, 13.1, 80.3)  # (min_lat, min_lng, max_lat, max_lng)
segments = get_traffic_data(bbox)

# Analyze route traffic
route = [(13.0827, 80.2707), (13.0850, 80.2750)]
traffic_info = get_route_traffic(route)
```

### 2. Frontend Integration

#### Add Traffic Layer to Map

```jsx
import TrafficLayer from './components/TrafficLayer';
import { MapContainer, TileLayer } from 'react-leaflet';

function MyMap() {
  const [showTraffic, setShowTraffic] = useState(true);

  return (
    <MapContainer center={[13.0827, 80.2707]} zoom={13}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      
      {/* Add traffic overlay */}
      <TrafficLayer 
        show={showTraffic}
        autoRefresh={true}
        refreshInterval={60000}  // 60 seconds
      />
    </MapContainer>
  );
}
```

#### Use Traffic API

```javascript
import trafficApi from './services/trafficApi';

// Get traffic for current map view
const bounds = {
  minLat: 13.0,
  minLng: 80.0,
  maxLat: 13.1,
  maxLng: 80.3
};
const segments = await trafficApi.getTrafficSegments(bounds);

// Analyze route traffic
const route = [[13.0827, 80.2707], [13.0850, 80.2750]];
const trafficInfo = await trafficApi.getRouteTraffic(route);

console.log(`Traffic level: ${trafficInfo.overall_level}`);
console.log(`Segments analyzed: ${trafficInfo.total_segments}`);

// Calculate time with traffic
const timeInfo = trafficApi.calculateTimeWithTraffic(
  10,  // 10 km
  60,  // 60 km/h free flow speed
  'MODERATE'  // traffic level
);

console.log(`Free flow: ${timeInfo.freeFlowMinutes} min`);
console.log(`With traffic: ${timeInfo.trafficMinutes} min`);
console.log(`Delay: ${timeInfo.delayMinutes} min`);
```

## Data Sources

### OpenTraffic
- **URL**: https://github.com/opentraffic
- **Type**: Real-time traffic speed data
- **Coverage**: Global (where data is available)
- **Update Frequency**: Real-time
- **License**: Open Data

### OpenStreetMap (Overpass API)
- **URL**: https://overpass-api.de
- **Type**: Road network data
- **Coverage**: Global
- **Update Frequency**: Community-updated
- **License**: ODbL (Open Database License)

## Traffic Estimation Algorithm

When real traffic data is unavailable, the system estimates traffic based on:

### 1. Road Type Speed Limits
- Motorway: 100 km/h
- Trunk: 80 km/h
- Primary: 60 km/h
- Secondary: 50 km/h
- Tertiary: 40 km/h
- Residential: 30 km/h

### 2. Peak Hour Detection
- Morning Peak: 8:00 AM - 10:00 AM
- Evening Peak: 5:00 PM - 8:00 PM

### 3. Congestion Factors (Peak Hours)
- Motorway: 60% of free flow
- Trunk: 65% of free flow
- Primary: 55% of free flow
- Secondary: 50% of free flow
- Tertiary: 60% of free flow
- Residential: 70% of free flow

### 4. Off-Peak
- All roads: 90% of free flow speed

## Performance

- **Cache Duration**: 5 minutes
- **API Timeout**: 10 seconds (OpenTraffic), 30 seconds (Overpass)
- **Retry Logic**: Up to 5 reconnection attempts
- **Fallback**: Always available via OSM estimation

## Configuration

### Environment Variables

```bash
# Backend (optional)
OPENTRAFFIC_API_URL=https://api.opentraffic.io
OVERPASS_API_URL=https://overpass-api.de/api/interpreter

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Customization

#### Adjust Cache Duration
```python
# backend/app/services/traffic_data.py
default_aggregator.cache_duration = timedelta(minutes=10)  # Change from 5 to 10 minutes
```

#### Change Refresh Interval
```jsx
<TrafficLayer 
  show={true}
  autoRefresh={true}
  refreshInterval={120000}  // 2 minutes instead of 1
/>
```

## Troubleshooting

### No Traffic Data Showing

1. **Check Service Status**
   ```bash
   curl http://localhost:8000/api/traffic/status
   ```

2. **Check Console Logs**
   - Backend: Look for `[Traffic]` messages
   - Frontend: Check browser console for errors

3. **Verify API Connectivity**
   - OpenTraffic: May not have data for all regions
   - Overpass: Rate-limited, may need to wait

### Slow Performance

1. **Increase Cache Duration** (reduce API calls)
2. **Disable Auto-refresh** when not needed
3. **Limit Map Zoom** to reduce segment count

### Inaccurate Estimates

- OSM estimation is time-based and may not reflect actual conditions
- Real traffic data from OpenTraffic is more accurate but may not be available everywhere
- Consider contributing to OpenTraffic project for better coverage!

## Future Enhancements

- [ ] Historical traffic patterns
- [ ] Machine learning-based prediction
- [ ] Integration with Google Traffic API (if available)
- [ ] Waze traffic data integration
- [ ] User-reported incidents
- [ ] Traffic prediction for future times

## Contributing

To improve traffic data accuracy:

1. **Contribute to OpenTraffic**: https://github.com/opentraffic
2. **Update OSM road data**: https://www.openstreetmap.org
3. **Report issues**: Create GitHub issues for bugs or improvements

## License

This traffic integration module is part of Smart Shield and follows the same license as the main project.

Traffic data sources have their own licenses:
- OpenTraffic: Open Data
- OpenStreetMap: ODbL (Open Database License)

---

**Built with ❤️ for safer deliveries**
