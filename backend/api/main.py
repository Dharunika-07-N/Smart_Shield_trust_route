from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.routes import (
    delivery, safety, feedback, traffic, auth, 
    training, users, deliveries, tracking, 
    dashboard, monitoring, experiments, ai_reports
)
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Smart Shield API",
    description="Backend API for Smart Shield Hospital Navigation and Safety Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create versioned router
api_v1_router = APIRouter(prefix="/api/v1")

# Register routes to the versioned router
api_v1_router.include_router(auth.router)
api_v1_router.include_router(delivery.router)
api_v1_router.include_router(deliveries.router)
api_v1_router.include_router(safety.router)
api_v1_router.include_router(feedback.router)
api_v1_router.include_router(traffic.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(training.router)
api_v1_router.include_router(tracking.router)
api_v1_router.include_router(dashboard.router)
api_v1_router.include_router(monitoring.router)
api_v1_router.include_router(experiments.router)
api_v1_router.include_router(ai_reports.router)

# Register the versioned router to the app
app.include_router(api_v1_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Smart Shield API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
