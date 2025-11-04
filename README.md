# 🛡️ AI Smart Shield Trust Route

AI-powered route optimization and safety system for delivery companies and riders in urban areas.

## 🎯 Project Overview

Smart Shield Trust Route is an intelligent delivery routing system that optimizes for delivery time, fuel efficiency, multi-delivery scheduling, and rider safety—especially for women riders during night hours.

## ✨ Key Features

- **AI Route Optimization Engine** - Combines graph algorithms + ML to plan efficient delivery sequences
- **Interactive Animated Map** - Snapchat-style location tracking with real-time route visualization
- **Safety Overlay** - Color-coded route segments based on safety scores with heatmap visualization
- **Crime Data Integration** - Tamil Nadu 2022 crime statistics for route safety scoring
- **Traffic-Aware Routing** - Real-time traffic data from Google Maps for accurate ETAs
- **Weather Integration** - Real-time weather conditions affecting route safety and duration
- **Multi-Delivery Handling** - Dynamic route updates for multiple stops
- **Smart Feedback System** - Rider ratings improve safety scoring over time
- **Company Dashboard** - Visualize delivery performance, safety heatmaps, and fuel metrics

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
- **Tamil Nadu Crime Data** - District-wise crime statistics (OpenCity.in)

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
│   │   │   ├── crime_data.py    # Tamil Nadu crime data service
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
│   │   └── crime/               # Place Tamil Nadu crime CSV files here
│   ├── scripts/
│   │   ├── setup_crime_data.py  # Helper script for crime data setup
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

3. Set up crime data (optional but recommended):
```bash
# Run the setup script to create data directory and sample CSV
python scripts/setup_crime_data.py

# Or manually download Tamil Nadu crime data:
# Visit: https://www.data.opencity.in/dataset/tamil-nadu-crime-data-2022
# Download CSV files and place in backend/data/crime/
```

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

3. **Crime Data** (No API key needed):
   - Download from [OpenCity.in](https://www.data.opencity.in/dataset/tamil-nadu-crime-data-2022)
   - Place CSV files in `backend/data/crime/`
   - Or use the built-in default data for development

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📊 Data Sources

### Crime Data
- **Tamil Nadu Crime Data 2022** - [OpenCity.in Dataset](https://www.data.opencity.in/dataset/tamil-nadu-crime-data-2022)
  - District-wise crime statistics
  - Includes murders, sexual harassment, road accidents, suicides
  - Public Domain license
  - Used for route safety scoring

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
- OpenCity.in for Tamil Nadu crime data
- OpenWeatherMap for weather data
- Coimbatore Institute of Technology for traffic research

## 📧 Contact

For questions or support, please open an issue on GitHub.

