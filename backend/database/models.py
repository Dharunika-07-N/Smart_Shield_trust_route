"""Database models."""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Route(Base):
    """Route model."""
    __tablename__ = "routes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    starting_point = Column(JSON, nullable=False)
    stops = Column(JSON, nullable=False)
    optimized_sequence = Column(JSON, nullable=True)
    total_distance_meters = Column(Float, nullable=False)
    total_duration_seconds = Column(Float, nullable=False)
    average_safety_score = Column(Float, nullable=False)
    total_fuel_liters = Column(Float, nullable=False)
    status = Column(String, default="pending")
    optimizations_applied = Column(JSON, default=list)
    estimated_arrivals = Column(JSON, nullable=True)
    rider_info = Column(JSON, nullable=True)
    vehicle_type = Column(String, default="motorcycle")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SafetyFeedback(Base):
    """Safety feedback model."""
    __tablename__ = "safety_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    route_id = Column(String, nullable=False, index=True)
    rider_id = Column(String, nullable=True)
    feedback_type = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    location = Column(JSON, nullable=True)
    comments = Column(Text, nullable=True)
    incident_type = Column(String, nullable=True)
    time_of_day = Column(String, default="day")
    date_submitted = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)


class SafetyScore(Base):
    """Stored safety scores."""
    __tablename__ = "safety_scores"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    coordinates = Column(JSON, nullable=False)
    overall_score = Column(Float, nullable=False)
    factors = Column(JSON, default=dict)
    risk_level = Column(String, nullable=False)
    time_of_day = Column(String, default="day")
    timestamp = Column(DateTime, default=datetime.utcnow)


class DeliveryCompany(Base):
    """Delivery company model."""
    __tablename__ = "delivery_companies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(JSON, nullable=True)
    subscription_tier = Column(String, default="basic")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Rider(Base):
    """Rider model."""
    __tablename__ = "riders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    company_id = Column(String, nullable=True, index=True)
    vehicle_type = Column(String, default="motorcycle")
    gender = Column(String, nullable=True)
    prefers_safe_routes = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

