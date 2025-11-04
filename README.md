# 🛡️ AI Smart Shield Trust Route

AI-powered route optimization and safety system for delivery companies and riders in urban areas.

## 🎯 Project Overview

Smart Shield Trust Route is an intelligent delivery routing system that optimizes for delivery time, fuel efficiency, multi-delivery scheduling, and rider safety—especially for women riders during night hours.

## ✨ Key Features

- **AI Route Optimization Engine** - Combines graph algorithms + ML to plan efficient delivery sequences
- **Safety Layer Integration** - Real-time crime data, lighting conditions, and patrol routes
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
- **Google Maps API** - Geocoding, directions
- **OpenStreetMap** - Map data
- **SafeGraph** - Safety/POI data

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
│   │   │   ├── maps.py          # Maps API integration
│   │   │   └── database.py      # Database operations
│   │   ├── schemas/             # Pydantic models
│   │   │   ├── delivery.py
│   │   │   └── safety.py
│   │   └── main.py              # FastAPI app
│   ├── database/
│   │   ├── models.py
│   │   └── database.py
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

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

4. Initialize database:
```bash
# Run database migrations
python -m api.services.database init_db
```

5. Start the FastAPI server:
```bash
uvicorn api.main:app --reload
```

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

```env
DATABASE_URL=postgresql://user:password@localhost/smartshield
GOOGLE_MAPS_API_KEY=your_key_here
MAPBOX_TOKEN=your_token_here
JWT_SECRET_KEY=your_secret_key
ENVIRONMENT=development
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Maps Platform
- OpenStreetMap contributors
- SafeGraph for safety data

## 📧 Contact

For questions or support, please open an issue on GitHub.

