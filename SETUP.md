# 🚀 Setup Guide

Complete setup instructions for AI Smart Shield Trust Route.

## Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **PostgreSQL 12+** with PostGIS extension ([Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/downloads))

### Optional
- **Google Maps API Key** ([Get Here](https://developers.google.com/maps/documentation/))
- **Mapbox Token** ([Get Here](https://account.mapbox.com/))

## Step-by-Step Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/smart-shield.git
cd smart-shield
```

### 2. Backend Setup

#### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3 Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/smartshield
GOOGLE_MAPS_API_KEY=your_key_here
MAPBOX_TOKEN=your_token_here
JWT_SECRET_KEY=your_secret_key_here
SECRET_KEY=another_secret_key_here
ENVIRONMENT=development
DEBUG=True
```

#### 2.4 Setup Database

**Create Database:**
```bash
createdb smartshield
```

**Connect to PostgreSQL:**
```bash
psql -U postgres -d smartshield
```

**Enable PostGIS extension:**
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
\q
```

#### 2.5 Initialize Database Tables

```bash
python -m api.services.database init_db
```

#### 2.6 Run Backend

```bash
python -m api.main
```

Backend will run on `http://localhost:8000`

Access API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### 3. Frontend Setup

#### 3.1 Install Dependencies

In a new terminal:
```bash
cd frontend
npm install
```

#### 3.2 Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAPBOX_TOKEN=your_mapbox_token_here
```

#### 3.3 Run Frontend

```bash
npm start
```

Frontend will run on `http://localhost:3000`

---

### 4. Verify Installation

#### 4.1 Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "database": "connected"
}
```

#### 4.2 Frontend Access

Open browser to `http://localhost:3000`

You should see the dashboard with sample data.

---

## Development Workflow

### Running Both Servers

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m api.main
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

### Making Changes

- Backend: Changes reload automatically with uvicorn `--reload`
- Frontend: React hot-reloads on file changes

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/
```

**Frontend:**
```bash
cd frontend
npm test
```

---

## Docker Setup (Alternative)

### Quick Start with Docker

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose File

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgis/postgis:12-3.0
    environment:
      POSTGRES_DB: smartshield
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/smartshield
    depends_on:
      - db
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

---

## Troubleshooting

### Backend Issues

**Database Connection Error:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# On Windows:
# Open Services and check PostgreSQL status
```

**Module Import Errors:**
```bash
# Make sure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Port Already in Use:**
```bash
# Find process using port 8000
lsof -i :8000  # On Linux/Mac
netstat -ano | findstr :8000  # On Windows

# Kill the process or change port in .env
```

### Frontend Issues

**Node Modules Errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS Errors:**
- Check backend `CORS_ORIGINS` in `config.py`
- Make sure backend is running on port 8000

**Blank Dashboard:**
- Check browser console for errors
- Verify API calls in Network tab
- Ensure backend is running and accessible

### Common Errors

**"No such file or directory: models/safety_scorer.h5"**
- This is normal on first run; model will be auto-generated
- Check `models/` directory was created

**"Could not load model"**
- Model will be created with synthetic data
- Check logs for warnings (not errors)

---

## Production Deployment

### Backend (FastAPI)

**Using Gunicorn:**
```bash
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**Using Docker:**
```bash
docker build -t smart-shield-backend ./backend
docker run -p 8000:8000 smart-shield-backend
```

### Frontend (React)

**Build for Production:**
```bash
cd frontend
npm run build
```

**Serve with Nginx:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | No | - |
| `MAPBOX_TOKEN` | Mapbox access token | No | - |
| `JWT_SECRET_KEY` | Secret for JWT tokens | Yes | - |
| `SECRET_KEY` | Application secret key | Yes | - |
| `ENVIRONMENT` | Environment (dev/staging/prod) | Yes | development |
| `DEBUG` | Debug mode | Yes | True |

### Frontend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `REACT_APP_API_URL` | Backend API URL | Yes |
| `REACT_APP_MAPBOX_TOKEN` | Mapbox token for maps | No |

---

## Next Steps

1. ✅ Setup complete!
2. 🎨 Customize dashboard theme
3. 🔑 Add API authentication
4. 🗺️ Configure mapping APIs
5. 📊 Integrate real data sources
6. 🚀 Deploy to production

---

## Getting Help

- 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md)
- 📚 Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- 🐛 Report issues on GitHub
- 💬 Join our Discord community

---

**Congratulations! You're ready to start optimizing delivery routes! 🎉**

