from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.routes import (
    delivery, safety, feedback, traffic, auth, 
    training, users, deliveries, tracking, 
    dashboard, monitoring, experiments, ai_reports, system
)
from api.utils.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from config.config import settings
import os
from dotenv import load_dotenv

import time
from fastapi import FastAPI, APIRouter, Request
...
import sys
from loguru import logger
import sentry_sdk

load_dotenv()

# Configure Logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr, 
    level=settings.LOG_LEVEL
)
logger.add(
    settings.LOG_FILE, 
    rotation="10 MB", 
    retention="10 days", 
    level=settings.LOG_LEVEL,
    compression="zip"
)

# Configure Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0 if settings.DEBUG else 0.1,
        profiles_sample_rate=1.0 if settings.DEBUG else 0.1,
    )
    logger.info("Sentry monitoring enabled.")

app = FastAPI(
    title="Smart Shield API",
    description="Backend API for Smart Shield Hospital Navigation and Safety Platform",
    version="1.0.0"
)

# Request Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # Use loguru for logging
    from loguru import logger
    logger.info(f"Request: {request.method} {request.url.path} - Process Time: {process_time:.4f}s")
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Add Limiter and Exception Handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
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
api_v1_router.include_router(system.router)

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
