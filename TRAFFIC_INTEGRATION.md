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
POST /api/traffic/route/analysis
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

### Backend (`backend/api/services/traffic.py`)

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

... existing content ...
