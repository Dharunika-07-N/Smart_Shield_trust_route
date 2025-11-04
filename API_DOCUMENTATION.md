# 📚 API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.smartshield.com
```

## Authentication
Currently, the API is open for development. In production, use JWT Bearer tokens:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Delivery Routes

#### Optimize Route
**POST** `/api/v1/delivery/optimize`

Optimize a delivery route with multiple objectives.

**Request Body:**
```json
{
  "starting_point": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "stops": [
    {
      "stop_id": "STOP001",
      "address": "123 Main St, New York, NY",
      "coordinates": {
        "latitude": 40.7210,
        "longitude": -74.0120
      },
      "priority": "high",
      "package_weight": 2.5,
      "special_instructions": "Ring twice"
    }
  ],
  "optimize_for": ["time", "distance", "fuel", "safety"],
  "rider_info": {
    "gender": "female",
    "prefers_safe_routes": true
  },
  "vehicle_type": "motorcycle",
  "avoid_highways": false,
  "avoid_tolls": false,
  "departure_time": "2024-01-15T09:00:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Route optimized successfully with 5 stops",
  "data": {
    "route_id": "ROUTE_1705314000",
    "total_distance_meters": 15000,
    "total_duration_seconds": 3600,
    "average_safety_score": 87.5,
    "total_fuel_liters": 1.275,
    "sequence": ["STOP001", "STOP002", "STOP003"],
    "segments": [
      {
        "from_stop": "START_0",
        "to_stop": "STOP001",
        "distance_meters": 3500,
        "duration_seconds": 900,
        "safety_score": 90.0,
        "estimated_fuel_liters": 0.2975
      }
    ],
    "optimizations_applied": ["time", "distance", "fuel", "safety"],
    "estimated_arrivals": {
      "STOP001": "2024-01-15T09:15:00",
      "STOP002": "2024-01-15T09:25:00"
    }
  }
}
```

**Status Codes:**
- `200 OK` - Route optimized successfully
- `400 Bad Request` - Invalid request data
- `500 Internal Server Error` - Optimization failed

---

#### Get Route
**GET** `/api/v1/delivery/routes/{route_id}`

Retrieve details of an existing route.

**Parameters:**
- `route_id` (path) - Unique route identifier

**Response:**
```json
{
  "success": true,
  "message": "Route retrieved successfully",
  "data": {
    "route_id": "ROUTE_1705314000",
    "total_distance_meters": 15000,
    "total_duration_seconds": 3600,
    "average_safety_score": 87.5,
    "total_fuel_liters": 1.275,
    "sequence": ["STOP001", "STOP002"],
    "segments": [],
    "optimizations_applied": ["time", "distance"],
    "estimated_arrivals": {}
  }
}
```

---

#### Update Route
**PUT** `/api/v1/delivery/routes/{route_id}`

Update an existing route (add/remove/reorder stops).

**Request Body:**
```json
{
  "action": "add_stop",
  "stop_id": "STOP003",
  "new_stop": {
    "stop_id": "STOP003",
    "address": "456 Oak Ave",
    "coordinates": {
      "latitude": 40.7285,
      "longitude": -74.0050
    },
    "priority": "medium"
  }
}
```

**Actions:**
- `add_stop` - Add a new stop to the route
- `remove_stop` - Remove a stop from the route
- `reorder` - Change the stop sequence

---

#### Delivery Statistics
**GET** `/api/v1/delivery/stats`

Get overall delivery statistics.

**Response:**
```json
{
  "total_routes": 1247,
  "total_distance_km": 15620.5,
  "average_delivery_time_minutes": 32,
  "fuel_saved_liters": 2400,
  "success_rate": 0.95
}
```

---

### 2. Safety Scoring

#### Calculate Safety Score
**POST** `/api/v1/safety/score`

Calculate safety scores for a route or location.

**Request Body:**
```json
{
  "coordinates": [
    {"latitude": 40.7128, "longitude": -74.0060},
    {"latitude": 40.7210, "longitude": -74.0120}
  ],
  "time_of_day": "night",
  "rider_gender": "female",
  "include_factors": true
}
```

**Response:**
```json
{
  "route_safety_score": 85.5,
  "average_score": 85.5,
  "segment_scores": [
    {
      "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
      "overall_score": 90.0,
      "factors": [
        {
          "factor": "crime",
          "score": 85.0,
          "weight": 0.35,
          "description": "Crime rate: 1.5"
        },
        {
          "factor": "lighting",
          "score": 75.0,
          "weight": 0.25,
          "description": "Lighting conditions: 75.0/100"
        }
      ],
      "risk_level": "low",
      "recommendations": []
    }
  ],
  "improvement_suggestions": [
    "Route is moderately safe",
    "Consider real-time safety updates"
  ]
}
```

---

#### Safety Heatmap
**POST** `/api/v1/safety/heatmap`

Generate safety heatmap data for a region.

**Request Body:**
```json
{
  "bounding_box": {
    "min_lat": 40.0,
    "max_lat": 41.0,
    "min_lon": -74.0,
    "max_lon": -73.0
  },
  "resolution": 100,
  "time_of_day": "day"
}
```

**Response:**
```json
{
  "heatmap_points": [
    {
      "coordinates": {"latitude": 40.5, "longitude": -73.5},
      "safety_score": 85.5,
      "density": 5
    }
  ],
  "min_score": 45.0,
  "max_score": 95.0,
  "average_score": 72.5
}
```

---

#### Safety Conditions
**POST** `/api/v1/safety/conditions/{location}`

Get detailed safety conditions at a specific location.

**Request Body:**
```json
{
  "location": {"latitude": 40.7128, "longitude": -74.0060},
  "time_of_day": "day"
}
```

**Response:**
```json
{
  "location": {"latitude": 40.7128, "longitude": -74.0060},
  "lighting_score": 85.0,
  "patrol_density": 75.5,
  "crime_incidents_recent": 2,
  "traffic_density": "medium",
  "nearby_establishments": ["Police Station", "24/7 Store"],
  "user_safety_rating": 4.2,
  "overall_score": 82.5,
  "recommendations": [
    "Route is moderately safe",
    "Consider real-time safety updates"
  ]
}
```

---

### 3. Feedback

#### Submit Feedback
**POST** `/api/v1/feedback/submit`

Submit rider feedback on route safety.

**Request Body:**
```json
{
  "route_id": "ROUTE_1705314000",
  "rider_id": "RIDER_456",
  "feedback_type": "safety",
  "rating": 5,
  "location": {"latitude": 40.7128, "longitude": -74.0060},
  "comments": "Well-lit route, felt very safe",
  "incident_type": null,
  "time_of_day": "night"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": "FB_789"
}
```

**Rating Scale:** 1-5 (1 = Very Unsafe, 5 = Very Safe)

---

#### Route Feedback
**POST** `/api/v1/feedback/route`

Submit overall feedback for a route.

**Request Body:**
```json
{
  "route_id": "ROUTE_1705314000",
  "overall_rating": 4.5,
  "delivery_time_accurate": true,
  "navigation_clear": true,
  "safety_concerns": [],
  "suggestions": "Could use better lighting in alley section"
}
```

---

#### Feedback Statistics
**GET** `/api/v1/feedback/stats`

Get aggregated feedback statistics.

**Response:**
```json
{
  "total_feedback": 452,
  "average_rating": 4.2,
  "feedback_by_type": {
    "safety": 250,
    "ease": 120,
    "accuracy": 82
  },
  "recent_trends": [],
  "safety_improvement_rate": 0.15
}
```

---

#### Get Route Feedback
**GET** `/api/v1/feedback/route/{route_id}`

Get feedback for a specific route.

**Response:**
```json
{
  "route_id": "ROUTE_1705314000",
  "feedback_count": 5,
  "average_rating": 4.4,
  "feedback": [
    {
      "rating": 5,
      "comments": "Excellent route",
      "time_of_day": "day"
    }
  ]
}
```

---

### 4. Health & Info

#### Root
**GET** `/`

**Response:**
```json
{
  "name": "AI Smart Shield Trust Route",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

---

#### Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "database": "connected"
}
```

---

## Error Responses

All error responses follow this format:
```json
{
  "error": "Error type",
  "detail": "Detailed error message"
}
```

**Common Status Codes:**
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limits

**Development:** Unlimited  
**Production:** 
- 100 requests/minute per API key
- 1000 requests/day per API key

## Example Usage

### Python
```python
import requests

url = "http://localhost:8000/api/v1/delivery/optimize"
payload = {
    "starting_point": {"latitude": 40.7128, "longitude": -74.0060},
    "stops": [
        {
            "stop_id": "STOP001",
            "address": "123 Main St",
            "coordinates": {"latitude": 40.7210, "longitude": -74.0120},
            "priority": "high"
        }
    ],
    "optimize_for": ["time", "safety"]
}

response = requests.post(url, json=payload)
print(response.json())
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/api/v1/delivery/optimize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(payload)
});

const data = await response.json();
console.log(data);
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/delivery/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "starting_point": {"latitude": 40.7128, "longitude": -74.0060},
    "stops": [{"stop_id": "STOP001", "address": "123 Main St", "coordinates": {"latitude": 40.7210, "longitude": -74.0120}}],
    "optimize_for": ["time", "safety"]
  }'
```

## Interactive Documentation

Visit `/docs` for Swagger UI interactive documentation.  
Visit `/redoc` for ReDoc documentation.

