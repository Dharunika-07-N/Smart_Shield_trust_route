# 🏗️ System Architecture

## Overview

AI Smart Shield Trust Route is built on a microservices-inspired architecture with clear separation between backend API, machine learning models, and frontend dashboard.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Dashboard (Port 3000)                             │   │
│  │  - Tailwind CSS for styling                              │   │
│  │  - Chart.js for analytics                                │   │
│  │  - Leaflet for maps                                      │   │
│  │  - React Router for navigation                           │   │
│  └───────────────────────┬──────────────────────────────────┘   │
└──────────────────────────┼───────────────────────────────────────┘
                           │ HTTPS/REST API
┌──────────────────────────┼───────────────────────────────────────┐
│                      BACKEND API LAYER                           │
│  ┌───────────────────────┼──────────────────────────────────┐   │
│  │  FastAPI Application (Port 8000)                         │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  Delivery    │  │   Safety     │  │   Feedback   │  │   │
│  │  │  Routes      │  │   Routes     │  │   Routes     │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │   │
│  │         │                  │                  │           │   │
│  │  ┌──────┴──────────────────┴──────────────────┴───────┐  │   │
│  │  │              Service Layer                           │  │   │
│  │  │  - MapsService (Google Maps/Mapbox)                 │  │   │
│  │  │  - DatabaseService (SQLAlchemy)                     │  │   │
│  │  └──────────────────────┬──────────────────────────────┘  │   │
│  │                         │                                   │   │
│  │  ┌──────────────────────┴──────────────────────────────┐  │   │
│  │  │              ML Models Layer                          │  │   │
│  │  │  - RouteOptimizer (OR-Tools + Genetic)              │  │   │
│  │  │  - SafetyScorer (Random Forest)                     │  │   │
│  │  └──────────────────────┬──────────────────────────────┘  │   │
│  └────────────────────────┼──────────────────────────────────┘   │
└────────────────────────────┼──────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐   ┌─────────────┐
│  PostgreSQL  │    │  Google Maps │   │  SafeGraph  │
│  + PostGIS   │    │     API      │   │     API     │
│              │    │              │   │             │
│  Routes      │    │  Geocoding   │   │  Crime Data │
│  Feedback    │    │  Directions  │   │  Safety Info│
│  Safety Data │    │  Distance    │   │             │
└──────────────┘    └──────────────┘   └─────────────┘
```

## Component Details

### 1. Frontend Layer (React)

**Technology Stack:**
- React 18 with functional components and hooks
- Tailwind CSS for styling
- Chart.js for data visualization
- Leaflet for interactive maps
- React Router for navigation

**Key Components:**
- `Dashboard.jsx` - Main dashboard with stats and navigation
- `Analytics.jsx` - Charts and performance metrics
- `RouteMap.jsx` - Interactive route visualization
- `SafetyHeatmap.jsx` - Safety score heatmap

**Features:**
- Real-time route visualization
- Performance analytics
- Safety heatmaps by time of day
- Responsive design for mobile and desktop

### 2. Backend API Layer (FastAPI)

**Technology Stack:**
- FastAPI for REST API
- SQLAlchemy for ORM
- Pydantic for data validation
- Loguru for logging

**API Endpoints:**

#### Delivery Routes (`/api/v1/delivery/`)
- `POST /optimize` - Optimize delivery route
- `GET /routes/{id}` - Get route details
- `PUT /routes/{id}` - Update route
- `GET /stats` - Delivery statistics

#### Safety Routes (`/api/v1/safety/`)
- `POST /score` - Calculate safety score
- `POST /heatmap` - Generate safety heatmap
- `POST /conditions/{location}` - Get safety conditions

#### Feedback Routes (`/api/v1/feedback/`)
- `POST /submit` - Submit rider feedback
- `POST /route` - Submit route feedback
- `GET /stats` - Feedback statistics

### 3. ML Models Layer

#### Route Optimizer
**Algorithm:** Hybrid approach using OR-Tools TSP solver + nearest neighbor fallback

**Objectives:**
- Minimize delivery time
- Minimize distance
- Minimize fuel consumption
- Maximize safety (especially for women riders)

**Features:**
- Multi-objective optimization
- Dynamic route updates
- Time window constraints
- Vehicle type considerations

#### Safety Scorer
**Model:** Random Forest Regressor

**Input Features:**
- Crime rate (0-10 scale)
- Lighting score (0-100)
- Patrol density (0-100)
- Traffic density (0-100)
- Time of day (hour 0-24)

**Output:** Safety score (0-100)

**Special Considerations:**
- Gender-specific adjustments for women riders
- Time-of-day weighting
- User feedback integration
- Continuous retraining

### 4. Data Layer

#### PostgreSQL with PostGIS
**Tables:**
- `routes` - Optimized delivery routes
- `safety_feedback` - Rider feedback data
- `safety_scores` - Cached safety scores
- `delivery_companies` - Company accounts
- `riders` - Rider profiles

**Features:**
- Geospatial queries with PostGIS
- JSON fields for flexible data
- Indexing for performance

### 5. External Services

#### Google Maps API
- Geocoding (address → coordinates)
- Reverse geocoding (coordinates → address)
- Distance matrix calculation
- Directions with waypoints
- Traffic-aware routing

#### SafeGraph API (Optional)
- Crime data by location
- Lighting conditions
- Patrol frequency

## Data Flow

### Route Optimization Flow

```
1. User submits delivery request (stops, objectives)
   ↓
2. Backend validates request with Pydantic
   ↓
3. MapsService fetches distances and directions
   ↓
4. SafetyScorer calculates safety scores for segments
   ↓
5. RouteOptimizer builds cost matrix
   ↓
6. OR-Tools optimizes route sequence
   ↓
7. Route segments are built with metadata
   ↓
8. Response sent to frontend with visualization data
   ↓
9. Route saved to database for analytics
```

### Safety Scoring Flow

```
1. Request with coordinates and time of day
   ↓
2. SafetyScorer extracts features per location
   ↓
3. Random Forest model predicts base score
   ↓
4. Gender-specific adjustments applied
   ↓
5. Safety factors calculated and weighted
   ↓
6. Risk level assigned (low/medium/high)
   ↓
7. Improvement suggestions generated
   ↓
8. Response with detailed breakdown
```

### Feedback Loop

```
1. Rider submits feedback after delivery
   ↓
2. Feedback saved to database
   ↓
3. SafetyScorer aggregates feedback by location
   ↓
4. When threshold reached (e.g., 10 new samples)
   ↓
5. Model retrained with new data
   ↓
6. Updated model improves future predictions
```

## Deployment Architecture

### Development
- Backend: Uvicorn with auto-reload
- Frontend: React development server
- Database: Local PostgreSQL or SQLite

### Production
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Nginx      │ ──▶ │   FastAPI    │ ──▶ │  PostgreSQL  │
│   Reverse    │     │   (Gunicorn) │     │  (AWS RDS)   │
│   Proxy      │     │              │     │              │
│              │     │              │     │              │
│  :443/80     │     │   Workers    │     │  Read Replica│
└──────────────┘     └──────────────┘     └──────────────┘
                            ▲
                            │
                     ┌──────────────┐
                     │  React App   │
                     │  (Vercel)    │
                     └──────────────┘
```

## Security Considerations

- JWT authentication for API access
- Rate limiting on public endpoints
- Input validation with Pydantic
- CORS configuration
- Environment-based secrets
- HTTPS in production
- SQL injection prevention (SQLAlchemy)
- XSS prevention (React)

## Scalability

### Horizontal Scaling
- Stateless API design
- Multiple FastAPI workers
- Database connection pooling
- Redis for caching

### Optimization Strategies
- Model caching for safety scores
- Batch processing for routes
- Lazy loading of map data
- CDN for frontend assets

## Monitoring & Observability

- Loguru for structured logging
- Application metrics
- Error tracking
- Performance monitoring
- Database query analysis

## Future Enhancements

1. Real-time GPS tracking
2. Predictive ETA with machine learning
3. Dynamic re-routing based on traffic
4. Weather integration
5. Multi-modal transportation
6. Blockchain for transparent delivery records
7. Mobile app (React Native)
8. Advanced ML models (Deep Learning)
9. IoT sensor integration
10. Voice navigation

