# 📂 Project Structure

Complete overview of the AI Smart Shield Trust Route project structure.

```
Smart_shield/
│
├── 📄 README.md                      # Main project documentation
├── 📄 ARCHITECTURE.md                # System architecture details
├── 📄 API_DOCUMENTATION.md           # Complete API reference
├── 📄 SETUP.md                       # Setup instructions
├── 📄 PROJECT_STRUCTURE.md           # This file
├── 📄 .gitignore                     # Git ignore rules
├── 📄 .env.example                   # Environment variables template
├── 🚀 setup.sh                       # Linux/Mac setup script
├── 🚀 setup.bat                      # Windows setup script
│
├── 🔧 backend/                       # Backend API (FastAPI)
│   ├── api/                          # API application code
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── routes/                   # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── delivery.py           # Delivery optimization endpoints
│   │   │   ├── safety.py             # Safety scoring endpoints
│   │   │   └── feedback.py           # Feedback endpoints
│   │   ├── models/                   # ML models
│   │   │   ├── __init__.py
│   │   │   ├── safety_scorer.py      # AI safety scoring model
│   │   │   └── route_optimizer.py    # Route optimization engine
│   │   ├── schemas/                  # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── delivery.py           # Delivery request/response models
│   │   │   ├── safety.py             # Safety models
│   │   │   └── feedback.py           # Feedback models
│   │   └── services/                 # Business logic services
│   │       ├── __init__.py
│   │       ├── maps.py               # Google Maps integration
│   │       └── database.py           # Database operations
│   │
│   ├── config/                       # Configuration
│   │   ├── __init__.py
│   │   └── config.py                 # App settings
│   │
│   ├── database/                     # Database models
│   │   ├── __init__.py
│   │   ├── database.py               # Database connection
│   │   └── models.py                 # SQLAlchemy models
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # Environment variables (gitignored)
│   │
│   └── models/                       # ML model cache (gitignored)
│       └── safety_scorer.h5         # Trained safety model
│
├── 🎨 frontend/                      # React Dashboard
│   ├── public/
│   │   ├── index.html                # HTML template
│   │   ├── manifest.json             # PWA manifest
│   │   └── favicon.ico               # App icon
│   │
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── __init__.py
│   │   │   ├── Dashboard.jsx         # Main dashboard
│   │   │   ├── Analytics.jsx         # Analytics charts
│   │   │   ├── RouteMap.jsx          # Route visualization
│   │   │   └── SafetyHeatmap.jsx     # Safety heatmap
│   │   ├── App.jsx                   # React app root
│   │   ├── App.css                   # App styles
│   │   ├── index.js                  # Entry point
│   │   └── index.css                 # Global styles
│   │
│   ├── package.json                  # Node dependencies
│   ├── tailwind.config.js            # Tailwind configuration
│   ├── postcss.config.js             # PostCSS config
│   ├── .env                          # Frontend env vars (gitignored)
│   │
│   └── build/                        # Production build (gitignored)
│
├── 📝 logs/                          # Application logs (gitignored)
└── 📝 .venv/                         # Virtual environment (gitignored)
```

## File Responsibilities

### Backend

#### `api/main.py`
- FastAPI application initialization
- CORS middleware configuration
- Router registration
- Error handlers
- Health check endpoints

#### `api/routes/delivery.py`
- POST `/api/v1/delivery/optimize` - Optimize delivery routes
- GET `/api/v1/delivery/routes/{id}` - Get route details
- PUT `/api/v1/delivery/routes/{id}` - Update routes
- GET `/api/v1/delivery/stats` - Delivery statistics

#### `api/routes/safety.py`
- POST `/api/v1/safety/score` - Calculate safety scores
- POST `/api/v1/safety/heatmap` - Generate heatmaps
- POST `/api/v1/safety/conditions/{location}` - Get conditions

#### `api/routes/feedback.py`
- POST `/api/v1/feedback/submit` - Submit rider feedback
- POST `/api/v1/feedback/route` - Submit route feedback
- GET `/api/v1/feedback/stats` - Feedback statistics

#### `api/models/safety_scorer.py`
- Random Forest regressor for safety prediction
- Feature engineering
- Model training and evaluation
- Gender-specific adjustments
- Continuous learning from feedback

#### `api/models/route_optimizer.py`
- Multi-objective TSP solver
- OR-Tools integration
- Cost matrix generation
- Route segment building
- ETA calculations

#### `api/services/maps.py`
- Google Maps API wrapper
- Geocoding and reverse geocoding
- Distance matrix calculation
- Directions API integration
- Mock data for development

#### `api/services/database.py`
- Database operations abstraction
- Route persistence
- Feedback storage
- Safety score caching

#### `database/models.py`
- SQLAlchemy ORM models
- Route, SafetyFeedback, SafetyScore tables
- DeliveryCompany, Rider tables

#### `config/config.py`
- Application settings
- Environment variable management
- Feature flags
- Default values

### Frontend

#### `src/components/Dashboard.jsx`
- Main dashboard UI
- Statistics cards
- Navigation tabs
- Recent activity feed
- Safety alerts

#### `src/components/Analytics.jsx`
- Chart.js visualizations
- Delivery time trends
- Fuel consumption charts
- Safety distribution
- Performance metrics

#### `src/components/RouteMap.jsx`
- Leaflet map integration
- Interactive route display
- Stop markers
- Route polylines
- Safety overlays

#### `src/components/SafetyHeatmap.jsx`
- Safety score visualization
- Color-coded zones
- Time-of-day filtering
- Heatmap statistics
- Legend display

#### `src/App.jsx`
- React Router setup
- Route definitions
- Global layout

#### Configuration Files
- `tailwind.config.js` - Custom Tailwind theme
- `postcss.config.js` - PostCSS processing
- `package.json` - Dependencies and scripts

## Data Flow

### Request Flow
```
User Action
  ↓
React Component
  ↓
Axios API Call
  ↓
FastAPI Endpoint
  ↓
Service Layer
  ↓
ML Models / Database
  ↓
Response JSON
  ↓
React State Update
  ↓
UI Re-render
```

### Route Optimization Flow
```
POST /delivery/optimize
  ↓
Validate Request (Pydantic)
  ↓
MapsService.get_distance_matrix()
  ↓
SafetyScorer.score_route()
  ↓
RouteOptimizer.optimize_route()
  ↓
Build Segments
  ↓
Save to Database
  ↓
Return OptimizedRoute
```

### Safety Scoring Flow
```
POST /safety/score
  ↓
Extract Features per Location
  ↓
Random Forest Prediction
  ↓
Apply Gender Adjustments
  ↓
Calculate Weighted Score
  ↓
Assign Risk Level
  ↓
Generate Suggestions
  ↓
Return SafetyData
```

## Configuration

### Environment Variables

**Backend** (`backend/.env`)
```
DATABASE_URL=postgresql://...
GOOGLE_MAPS_API_KEY=...
MAPBOX_TOKEN=...
JWT_SECRET_KEY=...
ENVIRONMENT=development
```

**Frontend** (`frontend/.env`)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAPBOX_TOKEN=...
```

## Dependencies

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- TensorFlow - ML models
- NetworkX - Graph algorithms
- OR-Tools - Optimization
- Google Maps API - Maps
- NumPy/Pandas - Data processing

### Frontend
- React - UI library
- Tailwind CSS - Styling
- Chart.js - Charts
- Leaflet - Maps
- React Router - Navigation
- Axios - HTTP client

## Scripts

### Backend
```bash
python -m api.main                    # Run server
pytest tests/                         # Run tests
python -m api.services.database init  # Init database
```

### Frontend
```bash
npm start                             # Dev server
npm run build                         # Production build
npm test                              # Run tests
```

## Deployment

### Development
- Backend: `localhost:8000`
- Frontend: `localhost:3000`

### Production
- Backend: Gunicorn + Uvicorn workers
- Frontend: Nginx + React build
- Database: PostgreSQL (AWS RDS)

## Testing Strategy

### Backend
- Unit tests for models
- Integration tests for routes
- Mock external APIs

### Frontend
- Component tests with Jest
- E2E tests with Cypress
- Visual regression tests

## Monitoring

### Backend
- Loguru logging
- Error tracking
- Performance metrics
- Database queries

### Frontend
- Error boundaries
- Console logging
- Performance monitoring

## Security

- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy)
- XSS prevention (React)
- CORS configuration
- JWT authentication
- Rate limiting

## Scaling Considerations

### Horizontal
- Stateless API
- Load balancer
- Database read replicas
- Redis caching

### Vertical
- Worker threads
- Connection pooling
- Memory optimization
- CDN for assets

