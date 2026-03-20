# 🛡️ AI Smart Shield Trust Route

AI-powered route optimization and safety system for delivery companies and riders in urban areas.

## 🎯 Project Overview

Smart Shield Trust Route is an intelligent delivery routing system that optimizes for delivery time, fuel efficiency, multi-delivery scheduling, and rider safety—especially for women riders during night hours.

## ✨ Key Features

- **AI Route Optimization Engine** - Combines graph algorithms + ML to plan efficient delivery sequences
- **Interactive Animated Map** - Snapchat-style location tracking with real-time route visualization
- **Safety Overlay** - Color-coded route segments based on safety scores with heatmap visualization
- **Hazard & Infrastructure Awareness** - Real-time assessment of lighting, traffic, and emergency service proximity for route safety scoring
- **Traffic-Aware Routing** - Real-time traffic data from Google Maps for accurate ETAs
- **Weather Integration** - Real-time weather conditions affecting route safety and duration
- **Multi-Delivery Handling** - Dynamic route updates for multiple stops
- **Smart Feedback System** - Rider ratings improve safety scoring over time
- **Company Dashboard** - Visualize delivery performance, safety heatmaps, and fuel metrics

## 🤖 AI Model Capabilities

Smart Shield Trust Route integrates several specialized AI/ML models to provide industry-leading safety and efficiency:

### 1. Safety Scoring Model (Random Forest)
Our safety engine uses a **Random Forest Regressor** trained on environmental hazards, infrastructure availability, and crowdsourced rider feedback. It evaluates locations based on key features including:
- Real-time lighting conditions and visibility
- Proximity to emergency services (Police stations, 24h hospitals)
- Road quality and traffic congestion levels
- Historical safety ratings from other riders

### 2. Multi-Objective Route Optimization
The routing engine uses high-performance graph algorithms (A* with custom heuristics) to solve the multi-objective TSP:
- **Primary Objective:** Maximize Safety Score (especially for night deliveries)
- **Secondary Objective:** Minimize distance/time and fuel consumption
- **Safety Deviation:** The system can intelligently deviate from the fastest route by up to 15% if it significantly improves the safety score.

### 3. Real-Time Feedback Loop
The system implements an online learning loop where every completed delivery and rider feedback entry is processed to:
- Dynamically update location safety scores based on rider perception
- Retrain models periodically to adapt to changing urban infrastructure/traffic patterns
- Identify emerging hazards before they are officially reported

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Dashboard                          │
│  (Delivery Analytics, Safety Heatmaps, Route Visualization)  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Route       │  │  Safety      │  │  Feedback    │      │
│  │  Optimizer   │  │  Scoring     │  │  System      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────┬────────────────┬──────────────────┬────────────────┘
         │                │                  │
         ▼                ▼                  ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────┐
│  PostgreSQL/   │ │  Maps API      │ │  ML Models   │
│  PostGIS       │ │  (Google Maps) │ │  (Safety)    │
│                │ │  (Mapbox)      │ │              │
└────────────────┘ └────────────────┘ └──────────────┘
```

## 🚀 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL/PostGIS** - Geospatial database
- **TensorFlow** - Machine learning models
- **NetworkX** - Graph algorithms for routing
- **NumPy/Pandas** - Data processing

### Frontend
- **React** - UI library
- **Tailwind CSS** - Styling
- **Chart.js** - Data visualization
- **Leaflet** - Interactive maps

### APIs & Services
- **Google Maps API** - Geocoding, traffic-aware directions, route geometry
- **OpenWeatherMap API** - Real-time weather data and hazard scoring
- **OpenStreetMap / Nominatim** - Map data and geocoding

## 📁 Project Structure

```
Smart_shield/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── delivery.py      # Delivery & route endpoints
│   │   │   ├── safety.py        # Safety scoring endpoints
│   │   │   └── feedback.py      # Rider feedback endpoints
│   │   ├── models/              # ML models
│   │   │   ├── safety_scorer.py
│   │   │   └── route_optimizer.py
│   │   ├── services/
│   │   │   ├── maps.py          # Maps API integration (traffic-aware)
│   │   │   ├── safety_service.py # Core safety and hazard service
│   │   │   ├── weather.py       # Weather API integration
│   │   │   └── database.py      # Database operations
│   │   ├── schemas/             # Pydantic models
│   │   │   ├── delivery.py
│   │   │   └── safety.py
│   │   └── main.py              # FastAPI app
│   ├── database/
│   │   ├── models.py
│   │   └── database.py
│   ├── data/
│   │   └── hazards/             # Place emergency infrastructure JSON here
│   ├── scripts/
│   │   ├── seed_safety_data.py  # Helper script for safety data seeding
│   │   └── README.md
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── RouteMap.jsx
│   │   │   ├── SafetyHeatmap.jsx
│   │   │   └── Analytics.jsx
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
├── config/
│   └── config.py
├── .env.example
├── .gitignore
└── README.md
```

## 🏃 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+ with PostGIS extension
- Google Maps API key (or Mapbox token)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up safety data (Heuristics + Real-time):
The system initializes with deterministic safety heuristics based on lighting, traffic, and infrastructure. Real-time data is pulled from Google Maps and OpenWeatherMap.

4. Set up environment variables:
```bash
# Create .env file from example
# On Windows PowerShell:
Copy-Item backend\.env.example backend\.env

# On Linux/Mac:
cp backend/.env.example backend/.env

# Edit .env with your API keys:
# - GOOGLE_MAPS_API_KEY (required for traffic-aware routing)
# - WEATHER_API_KEY (optional, has fallback to mock data)
```

5. Initialize database:
```bash
# Run database migrations
python -m api.services.database init_db
```

6. Start the FastAPI server:
```bash
cd backend
uvicorn api.main:app --reload
```

The server will start at `http://localhost:8000`
API documentation available at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

## 🔌 API Endpoints

### Route Optimization
- `POST /api/v1/delivery/optimize` - Optimize delivery route
- `GET /api/v1/delivery/routes/{route_id}` - Get route details
- `PUT /api/v1/delivery/routes/{route_id}` - Update route

### Safety Scoring
- `POST /api/v1/safety/score` - Calculate safety score
- `GET /api/v1/safety/heatmap` - Get safety heatmap data
- `GET /api/v1/safety/conditions/{location}` - Get safety conditions

### Feedback
- `POST /api/v1/feedback/submit` - Submit rider feedback
- `GET /api/v1/feedback/stats` - Get feedback statistics

## 📊 Success Metrics

- ✅ 20-30% reduction in delivery time
- ✅ 15-25% reduction in fuel usage
- ✅ 10-15% increase in delivery success rate
- ✅ Positive rider safety feedback, especially from women riders

## 🚀 Deployment

### 1. Docker Deployment (Recommended)
The easiest way to deploy the entire stack is using Docker Compose.

**Development:**
```bash
docker-compose up --build
```

**Production (includes PostgreSQL):**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Render Deployment
Smart Shield is designed to work seamlessly with [Render](https://render.com).

1. **Blueprint Deployment**: Connect your repo and Render will automatically detect the `render.yaml` file and set up:
   - Managed PostgreSQL database
   - FastAPI Backend (Web Service)
   - React Frontend (Static Site)

2. **Manual Setup**: Manually configure the web service and static site on Render following their documentation.

### 3. CI/CD
GitHub Actions is configured to:
- Run backend tests on PRs
- Build frontend production bundles
- Deploy to production on merge to `main` (if configured)

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
# Database (SQLite default, PostgreSQL for production)
DATABASE_URL=sqlite:///./smartshield.db

# Google Maps API (REQUIRED for traffic-aware routing)
# Get from: https://console.cloud.google.com/google/maps-apis
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Weather API (OPTIONAL - has fallback to mock data)
# Get from: https://openweathermap.org/api
WEATHER_API_KEY=your_weather_api_key_here

# Optional APIs
MAPBOX_TOKEN=your_mapbox_token_here
SAFEGRAPH_API_KEY=your_safegraph_api_key_here

# Security
SECRET_KEY=change-me-in-production
JWT_SECRET_KEY=change-me-in-production
ENVIRONMENT=development
```

### Getting API Keys

1. **Google Maps API Key** (Required for traffic-aware routing):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable "Maps JavaScript API" and "Directions API"
   - Create credentials → API Key
   - Copy the key to `GOOGLE_MAPS_API_KEY`

2. **Weather API Key** (Optional):
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your free API key
   - Copy to `WEATHER_API_KEY`

3. **Safety Data** (Infrastructure & Hazards):
   - Emergency service proximity (Hospitals, Police)
   - Real-time weather and lighting data
   - Historical hazard reports from the community

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📊 Data Sources

### Infrastructure & Safety Data
- **Emergency Infrastructure** - Proximity based on Google Maps / OSM
- **Lighting & Visibility** - Calculated based on time-of-day and weather
- **Road Safety** - Derived from traffic density and road quality metrics

### Traffic Data
- **Google Maps Directions API** - Traffic-aware routing
  - Real-time traffic conditions
  - Multiple route alternatives
  - Accurate ETAs based on current traffic

### Weather Data
- **OpenWeatherMap API** - Real-time weather conditions
  - Precipitation, wind, visibility
  - Weather hazard scoring
  - Route duration adjustments

### Research References
- **Coimbatore Traffic Congestion Study** - [GIS-based Traffic Analysis](https://www.sphinxsai.com/2017/ch_vol10_no8/2/%28382-387%29V10N8CT.pdf)
  - Traffic congestion evaluation methodology
  - Route optimization strategies

## 🙏 Acknowledgments

- Google Maps Platform for traffic-aware routing
- OpenStreetMap / Nominatim for map data and geocoding
- OpenWeatherMap for weather data
- Coimbatore Institute of Technology for traffic research

## 📧 Contact

For questions or support, please open an issue on GitHub.

