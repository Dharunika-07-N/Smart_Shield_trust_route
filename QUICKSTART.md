# ⚡ Quick Start Guide

Get AI Smart Shield Trust Route up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (optional - SQLite works for development)

## 🚀 Fast Setup

### Option 1: Automated Setup Script

**Linux/Mac:**
```bash
bash setup.sh
```

**Windows:**
```bash
setup.bat
```

### Option 2: Manual Setup

**1. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your settings
```

**2. Frontend Setup**
```bash
cd frontend
npm install
```

**3. Run Both Servers**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
python -m api.main
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

**4. Open Dashboard**
```
http://localhost:3000
```

## 🧪 Test the API

```bash
# Health check
curl http://localhost:8000/health

# Optimize a route
curl -X POST http://localhost:8000/api/v1/delivery/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "starting_point": {"latitude": 40.7128, "longitude": -74.0060},
    "stops": [{
      "stop_id": "STOP001",
      "address": "123 Main St, NY",
      "coordinates": {"latitude": 40.7210, "longitude": -74.0120}
    }],
    "optimize_for": ["time", "safety"]
  }'
```

## 📚 Next Steps

1. ✅ System running? Check `http://localhost:8000/docs` for API docs
2. 🎨 Explore the dashboard at `http://localhost:3000`
3. 🔑 Add your Google Maps API key to `.env`
4. 📖 Read [SETUP.md](SETUP.md) for detailed configuration
5. 🏗️ Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system

## 💡 Common Issues

**Port already in use?**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill  # Mac/Linux
# or change port in .env
```

**Module not found errors?**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Database errors?**
- For development, you can work without PostgreSQL
- The system will use in-memory storage if database is unavailable
- See [SETUP.md](SETUP.md) for database configuration

## 🎯 What You Can Do Now

- ✅ View dashboard analytics
- ✅ Calculate safety scores
- ✅ Generate heatmaps
- ✅ Optimize delivery routes
- ✅ Submit rider feedback

## 📞 Need Help?

- 📖 Full Setup: [SETUP.md](SETUP.md)
- 🏗️ Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- 📚 API Docs: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

**Ready to optimize delivery routes?** 🚚✨

