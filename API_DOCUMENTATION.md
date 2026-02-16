# 📚 Smart Shield API Documentation

## Complete API Reference

**Base URL:** `http://localhost:8000` (Development) | `https://api.yourdomain.com` (Production)

**API Version:** v1

**All endpoints are prefixed with:** `/api/v1`

---

## 🔐 Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Register User

**POST** `/api/v1/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "rider|admin|dispatcher|driver|customer",
  "phone": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "rider"
  }
}
```

**Errors:**
- `400 Bad Request` - Invalid input or user already exists
- `422 Unprocessable Entity` - Validation error

---

### Login

**POST** `/api/v1/auth/login`

Authenticate and receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1440,
  "user": {
    "id": 1,
    "username": "john_doe",
    "role": "rider"
  }
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `422 Unprocessable Entity` - Validation error

---

### Get Current User

**GET** `/api/v1/auth/me`

Get currently authenticated user details.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "rider",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 🚚 Delivery Management

### Optimize Route

**POST** `/api/v1/delivery/optimize`

Optimize delivery route using AI algorithms.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "pickup_location": {
    "lat": 13.0827,
    "lng": 80.2707,
    "address": "123 Main St, Chennai"
  },
  "delivery_locations": [
    {
      "lat": 13.0878,
      "lng": 80.2785,
      "address": "456 Oak Ave, Chennai",
      "priority": "high|normal|low",
      "time_window": {
        "start": "09:00",
        "end": "17:00"
      }
    }
  ],
  "rider_id": "string",
  "vehicle_type": "bike|car|van",
  "preferences": {
    "prioritize_safety": true,
    "avoid_tolls": false,
    "max_detour_percentage": 15
  }
}
```

**Response (200 OK):**
```json
{
  "route_id": "route_12345",
  "optimized_route": {
    "waypoints": [
      {
        "lat": 13.0827,
        "lng": 80.2707,
        "sequence": 0,
        "type": "pickup"
      },
      {
        "lat": 13.0878,
        "lng": 80.2785,
        "sequence": 1,
        "type": "delivery",
        "delivery_id": "del_001"
      }
    ],
    "polyline": "encoded_polyline_string"
  },
  "total_distance": 5.2,
  "total_distance_unit": "km",
  "estimated_time": 18,
  "estimated_time_unit": "minutes",
  "safety_score": 87.5,
  "fuel_estimate": 0.3,
  "fuel_estimate_unit": "liters",
  "cost_estimate": 45.50,
  "cost_estimate_currency": "INR",
  "alternative_routes": [
    {
      "distance": 5.8,
      "time": 22,
      "safety_score": 92.0,
      "description": "Safer route via Highway"
    }
  ]
}
```

**Errors:**
- `400 Bad Request` - Invalid location data
- `401 Unauthorized` - Missing or invalid token
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Route optimization failed

---

### Create Delivery

**POST** `/api/v1/delivery/create`

Create a new delivery request.

**Request Body:**
```json
{
  "customer_name": "string",
  "customer_phone": "string",
  "pickup_address": "string",
  "delivery_address": "string",
  "pickup_location": {
    "lat": 13.0827,
    "lng": 80.2707
  },
  "delivery_location": {
    "lat": 13.0878,
    "lng": 80.2785
  },
  "package_details": {
    "weight": 2.5,
    "dimensions": "30x20x15",
    "fragile": false
  },
  "priority": "high|normal|low",
  "scheduled_time": "2024-01-15T14:00:00Z (optional)"
}
```

**Response (201 Created):**
```json
{
  "delivery_id": "del_12345",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z",
  "estimated_pickup_time": "2024-01-15T11:00:00Z",
  "estimated_delivery_time": "2024-01-15T11:30:00Z"
}
```

---

### Get Delivery Details

**GET** `/api/v1/delivery/{delivery_id}`

Get details of a specific delivery.

**Response (200 OK):**
```json
{
  "delivery_id": "del_12345",
  "status": "in_transit|pending|delivered|cancelled",
  "customer_name": "John Doe",
  "pickup_address": "123 Main St",
  "delivery_address": "456 Oak Ave",
  "assigned_rider": {
    "id": "rider_001",
    "name": "Jane Smith",
    "phone": "+91 98765 43210"
  },
  "tracking": {
    "current_location": {
      "lat": 13.0850,
      "lng": 80.2750
    },
    "last_updated": "2024-01-15T11:15:00Z"
  },
  "timeline": [
    {
      "status": "created",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "status": "assigned",
      "timestamp": "2024-01-15T10:45:00Z"
    },
    {
      "status": "picked_up",
      "timestamp": "2024-01-15T11:00:00Z"
    }
  ]
}
```

---

## 🛡️ Safety Features

### Calculate Safety Score

**POST** `/api/v1/safety/score`

Calculate safety score for a location.

**Request Body:**
```json
{
  "location": {
    "lat": 13.0827,
    "lng": 80.2707
  },
  "time_of_day": "morning|afternoon|evening|night",
  "weather_conditions": "clear|rain|fog|storm",
  "rider_gender": "male|female|other (optional)"
}
```

**Response (200 OK):**
```json
{
  "safety_score": 87.5,
  "risk_level": "low|medium|high",
  "factors": {
    "crime_rate": 15.2,
    "lighting": 85.0,
    "police_presence": 70.0,
    "population_density": 65.0,
    "time_factor": 90.0
  },
  "nearest_safe_zones": [
    {
      "name": "Central Police Station",
      "type": "police_station",
      "distance": 0.8,
      "distance_unit": "km",
      "location": {
        "lat": 13.0835,
        "lng": 80.2715
      }
    }
  ],
  "recommendations": [
    "Well-lit area with good visibility",
    "Police station nearby",
    "Recommended for night deliveries"
  ],
  "warnings": []
}
```

---

### Get Safety Heatmap

**GET** `/api/v1/safety/heatmap`

Get safety heatmap data for a geographic area.

**Query Parameters:**
- `bounds` (required): `min_lat,min_lng,max_lat,max_lng`
- `resolution` (optional): `low|medium|high` (default: medium)
- `time_of_day` (optional): `morning|afternoon|evening|night`

**Example:**
```
GET /api/v1/safety/heatmap?bounds=13.0,80.0,13.2,80.4&resolution=medium&time_of_day=night
```

**Response (200 OK):**
```json
{
  "heatmap_data": [
    {
      "lat": 13.0827,
      "lng": 80.2707,
      "safety_score": 87.5,
      "intensity": 0.875
    },
    {
      "lat": 13.0878,
      "lng": 80.2785,
      "safety_score": 92.0,
      "intensity": 0.920
    }
  ],
  "legend": {
    "high_safety": ">= 80",
    "medium_safety": "60-79",
    "low_safety": "< 60"
  },
  "metadata": {
    "total_points": 150,
    "average_safety": 85.3,
    "last_updated": "2024-01-15T10:00:00Z"
  }
}
```

---

### Submit Safety Feedback

**POST** `/api/v1/feedback/safety`

Submit safety feedback for a location.

**Request Body:**
```json
{
  "location": {
    "lat": 13.0827,
    "lng": 80.2707
  },
  "rider_id": "rider_001",
  "route_id": "route_12345",
  "safety_rating": 4,
  "incident_type": "none|harassment|theft|accident|other",
  "description": "Well-lit area, felt safe",
  "time_of_incident": "2024-01-15T20:30:00Z",
  "anonymous": false
}
```

**Response (201 Created):**
```json
{
  "feedback_id": "fb_12345",
  "status": "submitted",
  "message": "Thank you for your feedback. This helps improve safety for all riders."
}
```

---

## 🚦 Traffic Information

### Get Traffic Conditions

**GET** `/api/v1/traffic/conditions`

Get real-time traffic conditions.

**Query Parameters:**
- `location`: `lat,lng`
- `radius`: radius in km (default: 5)

**Response (200 OK):**
```json
{
  "location": {
    "lat": 13.0827,
    "lng": 80.2707
  },
  "traffic_level": "low|moderate|heavy|severe",
  "average_speed": 35.5,
  "speed_unit": "km/h",
  "congestion_percentage": 25,
  "incidents": [
    {
      "type": "accident|construction|event",
      "location": {
        "lat": 13.0850,
        "lng": 80.2750
      },
      "description": "Minor accident on Main Road",
      "severity": "low|medium|high",
      "reported_at": "2024-01-15T11:00:00Z"
    }
  ],
  "last_updated": "2024-01-15T11:15:00Z"
}
```

---

## 🤖 AI Reports

### Generate Executive Dashboard Summary

**POST** `/api/v1/ai/reports/executive-dashboard`

Generate AI-powered executive summary.

**Request Body:**
```json
{
  "time_period": "daily|weekly|monthly",
  "provider": "openai|anthropic|gemini",
  "format": "json|markdown|html"
}
```

**Response (200 OK):**
```json
{
  "summary": {
    "title": "Weekly Executive Dashboard Summary",
    "generated_at": "2024-01-15T10:30:00Z",
    "time_period": "2024-01-08 to 2024-01-15",
    "key_insights": [
      "Total deliveries increased by 15% compared to last week",
      "Average safety score improved to 87.5%",
      "Fuel efficiency improved by 12%"
    ],
    "metrics": {
      "total_deliveries": 1250,
      "successful_deliveries": 1180,
      "success_rate": 94.4,
      "average_delivery_time": 18.5,
      "total_distance": 5420,
      "fuel_saved": 245.5
    },
    "recommendations": [
      "Continue prioritizing safety-optimized routes",
      "Consider expanding service to high-demand areas",
      "Implement driver training program for efficiency"
    ],
    "alerts": [
      "3 safety incidents reported in Zone B - requires attention"
    ]
  },
  "provider": "gemini",
  "format": "json"
}
```

---

### Generate User Activity Summary

**POST** `/api/v1/ai/reports/user-summary`

Generate AI summary of user activity.

**Request Body:**
```json
{
  "time_period": "daily|weekly|monthly",
  "provider": "openai|anthropic|gemini",
  "format": "json|markdown|html"
}
```

**Response:** Similar structure to executive dashboard

---

### Generate Rider Performance Summary

**POST** `/api/v1/ai/reports/rider-summary`

Generate AI summary of rider performance.

---

### Generate Feedback Analysis

**POST** `/api/v1/ai/reports/feedback-summary`

Generate AI analysis of user feedback.

---

### Generate ML Model Performance Report

**POST** `/api/v1/ai/reports/ml-performance`

Generate AI report on ML model performance.

---

## 📊 Dashboard & Analytics

### Get Dashboard Stats

**GET** `/api/v1/dashboard/stats`

Get dashboard statistics for current user.

**Query Parameters:**
- `rider_id` (optional): Specific rider ID
- `time_period` (optional): `today|week|month`

**Response (200 OK):**
```json
{
  "active_deliveries": {
    "value": "12",
    "subValue": "4 in transit",
    "trend": "+8% vs last week"
  },
  "safety_score": {
    "value": "87%",
    "subValue": "Above average",
    "trend": "+5% vs last week"
  },
  "fuel_saved": {
    "value": "24.5L",
    "subValue": "This week",
    "trend": "+12% vs last week"
  },
  "avg_delivery_time": {
    "value": "18 min",
    "subValue": "Target: 20 min",
    "trend": "+3% vs last week"
  }
}
```

---

### Get Delivery Queue

**GET** `/api/v1/dashboard/delivery-queue`

Get pending deliveries for rider.

**Query Parameters:**
- `limit` (optional): Number of deliveries to return (default: 10)
- `status` (optional): Filter by status

**Response (200 OK):**
```json
[
  {
    "id": "del_001",
    "customer_name": "John Doe",
    "address": "123 Main St, Chennai",
    "priority": "High|Normal|Urgent",
    "status": "pending|assigned|in_transit",
    "safety_score": 85,
    "distance": "3.2 km",
    "estimated_time": "12 min",
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

---

### Get Zone Safety Data

**GET** `/api/v1/dashboard/zone-safety`

Get safety data for different zones.

**Response (200 OK):**
```json
[
  {
    "name": "Zone A - Downtown",
    "score": 92,
    "color": "green|amber|red",
    "incidents": "2 incidents this week",
    "trend": "down|up|stable"
  }
]
```

---

### Get Weather Data

**GET** `/api/v1/dashboard/weather`

Get current weather conditions.

**Query Parameters:**
- `location` (optional): `lat,lng` (defaults to user location)

**Response (200 OK):**
```json
{
  "temperature": 28,
  "temperature_unit": "celsius",
  "condition": "Clear|Cloudy|Rainy|Stormy",
  "icon": "☀️",
  "humidity": 65,
  "wind_speed": 12,
  "wind_speed_unit": "km/h",
  "visibility": "Good",
  "impact": "Low|Medium|High",
  "last_updated": "2024-01-15T11:00:00Z"
}
```

---

## 🚨 Emergency & Alerts

### Trigger Panic Button

**POST** `/api/v1/emergency/panic`

Trigger emergency panic alert.

**Request Body:**
```json
{
  "rider_id": "rider_001",
  "location": {
    "lat": 13.0827,
    "lng": 80.2707
  },
  "route_id": "route_12345 (optional)",
  "delivery_id": "del_12345 (optional)",
  "notes": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "alert_id": "alert_12345",
  "status": "active",
  "emergency_contacts_notified": [
    "Police - 100",
    "Emergency Contact - +91 98765 43210"
  ],
  "nearest_safe_zone": {
    "name": "Central Police Station",
    "distance": 0.8,
    "eta": "3 minutes"
  },
  "message": "Emergency alert activated. Help is on the way."
}
```

---

### Resolve Panic Alert

**POST** `/api/v1/emergency/resolve`

Mark panic alert as resolved.

**Request Body:**
```json
{
  "alert_id": "alert_12345",
  "rider_id": "rider_001",
  "resolution_notes": "False alarm / Situation resolved"
}
```

**Response (200 OK):**
```json
{
  "alert_id": "alert_12345",
  "status": "resolved",
  "resolved_at": "2024-01-15T11:30:00Z",
  "message": "Alert resolved successfully"
}
```

---

### Get Recent Alerts

**GET** `/api/v1/emergency/alerts`

Get recent emergency alerts.

**Query Parameters:**
- `status` (optional): `active|resolved|all`
- `limit` (optional): Number of alerts (default: 10)

**Response (200 OK):**
```json
[
  {
    "alert_id": "alert_12345",
    "rider_id": "rider_001",
    "type": "panic|safety|accident",
    "status": "active|resolved",
    "location": {
      "lat": 13.0827,
      "lng": 80.2707
    },
    "created_at": "2024-01-15T11:00:00Z",
    "resolved_at": null,
    "title": "Emergency Alert",
    "message": "Panic button activated by rider"
  }
]
```

---

## 📈 Rate Limiting

All endpoints are rate-limited to prevent abuse:

- **Standard endpoints:** 60 requests per minute per user
- **AI endpoints:** 10 requests per minute per user
- **Authentication endpoints:** 5 requests per minute per IP

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642248000
```

**Rate Limit Exceeded (429):**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again in 30 seconds.",
  "retry_after": 30
}
```

---

## ❌ Error Responses

### Standard Error Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional error details"
  },
  "timestamp": "2024-01-15T11:00:00Z"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## 🔧 Pagination

List endpoints support pagination:

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20, max: 100)

**Response includes:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 🌐 WebSocket Endpoints

### Real-time Tracking

**WebSocket URL:** `ws://localhost:8000/ws/tracking/{delivery_id}`

**Messages:**
```json
{
  "type": "location_update",
  "delivery_id": "del_12345",
  "location": {
    "lat": 13.0827,
    "lng": 80.2707
  },
  "timestamp": "2024-01-15T11:00:00Z"
}
```

---

## 📝 API Changelog

### Version 1.0.0 (2024-01-15)
- Initial API release
- Authentication endpoints
- Delivery management
- Safety features
- AI-powered reports
- Real-time tracking

---

## 🔗 Additional Resources

- **Interactive API Docs:** `https://api.yourdomain.com/docs`
- **OpenAPI Spec:** `https://api.yourdomain.com/openapi.json`
- **Postman Collection:** Available on request
- **Support:** support@smartshield.com

---

**API Documentation v1.0.0** | Last Updated: 2024-01-15
