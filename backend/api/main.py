from fastapi import FastAPI
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

# Register routes
app.include_router(auth.router)
app.include_router(delivery.router)
app.include_router(deliveries.router)
app.include_router(safety.router)
app.include_router(feedback.router)
app.include_router(traffic.router)
app.include_router(users.router)
app.include_router(training.router)
app.include_router(tracking.router)
app.include_router(dashboard.router)
app.include_router(monitoring.router)
app.include_router(experiments.router)
app.include_router(ai_reports.router)

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
