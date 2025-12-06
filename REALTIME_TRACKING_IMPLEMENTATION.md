# Real-Time Tracking & Live Updates Implementation

## Overview
This document describes the implementation of real-time delivery tracking with live location updates using WebSockets.

## Backend Implementation

### 1. Database Model
- **File**: `backend/database/models.py`
- **Model**: `DeliveryStatus`
- **Fields**:
  - `id`: Unique identifier
  - `delivery_id`: Delivery identifier (indexed)
  - `route_id`: Associated route (indexed)
  - `rider_id`: Rider identifier (indexed)
  - `current_location`: JSON with latitude/longitude
  - `status`: pending, in_transit, delivered, failed, cancelled
  - `timestamp`: When the update was recorded (indexed)
  - `speed_kmh`: Current speed in km/h
  - `heading`: Direction in degrees (0-360)
  - `battery_level`: Device battery level (0-100)

### 2. API Endpoints

#### POST `/api/v1/delivery/location-update`
- **Purpose**: Rider sends GPS coordinates every 30 seconds
- **Request Body**:
  ```json
  {
    "delivery_id": "DELIVERY_123",
    "route_id": "ROUTE_456",
    "rider_id": "RIDER_789",
    "current_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "status": "in_transit",
    "speed_kmh": 45.5,
    "heading": 180.0,
    "battery_level": 85
  }
  ```
- **Response**: Success confirmation with update ID and timestamp
- **Behavior**: Saves location to database and broadcasts to all connected WebSocket clients

#### GET `/api/v1/delivery/{delivery_id}/track`
- **Purpose**: Customer/company retrieves delivery tracking information
- **Response**: 
  ```json
  {
    "success": true,
    "message": "Tracking data retrieved successfully",
    "data": {
      "delivery_id": "DELIVERY_123",
      "current_location": {
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "status": "in_transit",
      "timestamp": "2024-01-01T12:00:00",
      "speed_kmh": 45.5,
      "heading": 180.0,
      "location_history": [...]
    }
  }
  ```

#### WebSocket `/api/v1/delivery/{delivery_id}/ws`
- **Purpose**: Real-time location updates for tracking clients
- **Connection**: Clients connect to receive live updates
- **Messages Sent**:
  - `initial_location`: Sent immediately upon connection with latest location
  - `location_update`: Sent whenever rider sends new coordinates
  - `pong`: Response to client ping messages
- **Message Format**:
  ```json
  {
    "type": "location_update",
    "delivery_id": "DELIVERY_123",
    "timestamp": "2024-01-01T12:00:00",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "status": "in_transit",
    "speed_kmh": 45.5,
    "heading": 180.0,
    "battery_level": 85
  }
  ```

### 3. WebSocket Connection Manager
- **File**: `backend/api/routes/delivery.py`
- **Class**: `ConnectionManager`
- **Features**:
  - Manages multiple WebSocket connections per delivery
  - Broadcasts location updates to all connected clients
  - Handles connection/disconnection gracefully
  - Auto-cleans disconnected clients

### 4. Database Service Methods
- **File**: `backend/api/services/database.py`
- **Methods Added**:
  - `save_location_update()`: Save location update to database
  - `get_delivery_tracking()`: Get tracking data with location history
  - `get_latest_location()`: Get most recent location for a delivery

## Frontend Implementation

### 1. LiveTracking Component
- **File**: `frontend/src/components/LiveTracking.jsx`
- **Features**:
  - Real-time map showing rider's current position
  - Location history path visualization
  - Status indicators (connected/disconnected)
  - Speed, heading, and battery level display
  - Two modes:
    - **Tracking Mode** (default): For customers/companies to track deliveries
    - **Rider Mode**: For riders to share their location (set `isRider={true}`)

### 2. API Service Updates
- **File**: `frontend/src/services/api.js`
- **Methods Added**:
  - `updateLocation(data)`: Send location update from rider
  - `trackDelivery(deliveryId)`: Get delivery tracking data

### 3. Dashboard Integration
- **File**: `frontend/src/components/Dashboard.jsx`
- **Added**: "Live Tracking" tab in navigation

## Usage

### For Riders (Sharing Location)
1. Navigate to Dashboard → Live Tracking
2. Enter your delivery ID
3. The component will automatically:
   - Request location permissions
   - Get GPS coordinates
   - Send updates to server every 30 seconds
   - Display your current location on the map

### For Customers/Companies (Tracking Deliveries)
1. Navigate to Dashboard → Live Tracking
2. Enter the delivery ID you want to track
3. The component will:
   - Connect to WebSocket for real-time updates
   - Display current location on map
   - Show location history path
   - Display status, speed, heading, and battery level

## Technical Details

### Location Update Frequency
- Riders send updates every **30 seconds**
- WebSocket clients receive updates in real-time as they're sent

### Data Persistence
- All location updates are saved to the `delivery_status` table
- Location history is available via the tracking endpoint
- History is limited to last 100 points in the frontend for performance

### WebSocket Reconnection
- Clients automatically attempt to reconnect if connection is lost
- Reconnection happens after 3 seconds of disconnection

### Browser Compatibility
- Requires browsers with WebSocket support (all modern browsers)
- Requires Geolocation API for rider mode
- Requires user permission for location access

## Database Migration
The new `delivery_status` table will be automatically created when the application starts (via SQLAlchemy's `create_all()`).

## Testing

### Test Location Update Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/delivery/location-update \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_id": "TEST_123",
    "current_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "status": "in_transit"
  }'
```

### Test Tracking Endpoint
```bash
curl http://localhost:8000/api/v1/delivery/TEST_123/track
```

### Test WebSocket Connection
Use a WebSocket client tool or browser console:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/delivery/TEST_123/ws');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Future Enhancements
- Add authentication/authorization for tracking endpoints
- Implement geofencing alerts
- Add delivery ETA calculations
- Implement route deviation alerts
- Add historical analytics for delivery patterns
- Support for multiple simultaneous deliveries per rider
