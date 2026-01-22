"""Main FastAPI application."""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import delivery, safety, feedback, traffic, auth, training, users, deliveries, tracking
from api.services.database import init_db
import os
from loguru import logger

app = FastAPI(
    title="Smart Shield Trust Route API",
    description="AI-powered route optimization and safety system",
    version="2.0.0"
)

# CORS configuration
# Using the list from environment or defaulting to all for development
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Note: Keeping the /api/v1 prefix to ensure compatibility with the frontend
app.include_router(delivery.router, prefix="/api/v1", tags=["Delivery"])
app.include_router(safety.router, prefix="/api/v1", tags=["Safety"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])
app.include_router(traffic.router, prefix="/api/v1", tags=["Traffic"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(training.router, prefix="/api/v1", tags=["Training"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(deliveries.router, prefix="/api/v1", tags=["Deliveries"])
app.include_router(tracking.router, prefix="/api/v1", tags=["Tracking"])



@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Smart Shield Trust Route API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

@app.get("/")
async def root():
    return {
        "message": "Smart Shield Trust Route API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
