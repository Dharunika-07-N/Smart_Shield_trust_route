"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.config import settings
from loguru import logger

# Database URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Handle Render's 'postgres://' format which SQLAlchemy needs as 'postgresql://'
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
# Use static pool for SQLite, connection pooling for PostgreSQL
if "sqlite" in SQLALCHEMY_DATABASE_URL.lower():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database tables."""
    try:
        # Import all models here to ensure they're registered
        from database.models import Route, SafetyFeedback, SafetyScore, DeliveryCompany, Rider, DeliveryStatus, RouteMonitoring, PanicAlert, RiderCheckIn, SafeZone, RideAlong, User, DeliveryRoute, RouteSegment, CrimeData, DeliveryFeedback, HistoricalDelivery, CrowdsourcedAlert, RiderProfile, DriverProfile, UserSession, Delivery, DeliveryBatch, DeliveryProof, Customer, BuddyPair
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # In development, we can work without database
        if settings.DEBUG:
            logger.warning("Continuing without database connection")
        else:
            raise


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

