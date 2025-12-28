"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.config import settings
from api.routes import delivery, safety, feedback, traffic, auth
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from api.services.database import init_db
import uvicorn
from loguru import logger

# Configure logging
logger.add(
    settings.LOG_FILE,
    rotation="10 MB",
    retention="7 days",
    level=settings.LOG_LEVEL
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered route optimization and safety system for delivery companies",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger.info(f"Setting up API in {settings.ENVIRONMENT} mode")

# CORS middleware - Setup as early as possible
if settings.ENVIRONMENT == "development":
    logger.info("Enabling permissive CORS for development")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

# Include routers
app.include_router(delivery.router, prefix=settings.API_V1_PREFIX, tags=["Delivery"])
app.include_router(safety.router, prefix=settings.API_V1_PREFIX, tags=["Safety"])
app.include_router(feedback.router, prefix=settings.API_V1_PREFIX, tags=["Feedback"])
app.include_router(traffic.router, prefix=settings.API_V1_PREFIX, tags=["Traffic"])
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and other services on startup."""
    logger.info("Starting AI Smart Shield Trust Route API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

