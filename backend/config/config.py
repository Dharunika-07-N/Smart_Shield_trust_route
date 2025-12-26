"""Configuration settings for the application."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings."""
    
    # Project Info
    PROJECT_NAME: str = "AI Smart Shield Trust Route"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./smartshield.db"  # Default to SQLite for easy setup
    )
    
    # API Keys
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    MAPBOX_TOKEN: str = os.getenv("MAPBOX_TOKEN", "")
    SAFEGRAPH_API_KEY: str = os.getenv("SAFEGRAPH_API_KEY", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
    ]
    
    # Server
    HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Route Optimization
    MAX_DELIVERY_STOPS: int = 50
    OPTIMIZATION_ALGORITHM: str = os.getenv("OPTIMIZATION_ALGORITHM", "nearest_neighbor")  # hybrid, genetic, nearest_neighbor
    
    # Safety Scoring
    SAFETY_WEIGHTS: dict = {
        "crime": 0.35,
        "lighting": 0.25,
        "patrol_presence": 0.25,
        "traffic": 0.10,
        "user_feedback": 0.05
    }
    
    # Time Windows
    DEFAULT_TIME_WINDOW_MINUTES: int = 15
    
    # Fuel Efficiency
    FUEL_CONSUMPTION_PER_KM: float = 0.085  # liters per km (average for delivery vehicles)
    
    # Maps & Geocoding
    MAX_GEOCODE_RETRIES: int = 3
    GEOCODE_CACHE_TTL: int = 3600  # seconds
    
    # ML Models
    MODEL_CACHE_DIR: Path = Path("models/cache")
    SAFETY_MODEL_PATH: str = "models/safety_scorer.h5"
    SAFETY_SCALER_PATH: str = "models/safety_scaler.pkl"
    
    # Feedback System
    MIN_FEEDBACK_SAMPLES: int = 5  # Minimum samples before retraining
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Email Configuration (for SOS alerts)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "dharunikaktm@gmail.com")
    EMERGENCY_EMAIL: str = os.getenv("EMERGENCY_EMAIL", "dharunikaktm@gmail.com")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

# Create global settings instance
settings = Settings()

# Ensure directories exist
settings.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)

