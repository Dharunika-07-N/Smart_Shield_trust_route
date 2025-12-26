"""Database models."""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from database.database import Base
from datetime import datetime
import uuid


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
    emergency_contacts = Column(JSON, nullable=True)  # List of {name, phone, email, relationship}
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class DeliveryStatus(Base):
    """Delivery status tracking model."""
    __tablename__ = "delivery_status"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    delivery_id = Column(String, nullable=False, index=True)
    route_id = Column(String, nullable=True, index=True)
    rider_id = Column(String, nullable=True, index=True)
    current_location = Column(JSON, nullable=False)  # {latitude, longitude}
    status = Column(String, nullable=False, default="pending")  # pending, in_transit, delivered, failed, cancelled
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    speed_kmh = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)  # Direction in degrees (0-360)
    battery_level = Column(Integer, nullable=True)  # For mobile devices
    created_at = Column(DateTime, default=datetime.utcnow)


class RouteMonitoring(Base):
    """Route monitoring for deviation detection."""
    __tablename__ = "route_monitoring"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    route_id = Column(String, nullable=False, index=True)
    rider_id = Column(String, nullable=True, index=True)
    delivery_id = Column(String, nullable=True, index=True)
    planned_location = Column(JSON, nullable=False)  # Expected location at this time
    actual_location = Column(JSON, nullable=False)  # Actual rider location
    deviation_meters = Column(Float, nullable=False)  # Distance from planned route
    time_delay_seconds = Column(Float, nullable=True)  # Time delay vs planned
    requires_reoptimization = Column(Boolean, default=False)
    reoptimized_at = Column(DateTime, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class PanicAlert(Base):
    """Panic button alerts."""
    __tablename__ = "panic_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rider_id = Column(String, nullable=False, index=True)
    route_id = Column(String, nullable=True, index=True)
    delivery_id = Column(String, nullable=True, index=True)
    location = Column(JSON, nullable=False)  # {latitude, longitude}
    status = Column(String, default="active")  # active, acknowledged, resolved
    alerted_contacts = Column(JSON, nullable=True)  # List of contacted emergency contacts
    company_notified = Column(Boolean, default=False)
    emergency_services_notified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)


class RiderCheckIn(Base):
    """Rider check-in system for night shifts."""
    __tablename__ = "rider_checkins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rider_id = Column(String, nullable=False, index=True)
    route_id = Column(String, nullable=True, index=True)
    delivery_id = Column(String, nullable=True, index=True)
    location = Column(JSON, nullable=False)  # {latitude, longitude}
    check_in_type = Column(String, default="scheduled")  # scheduled, manual, missed
    is_night_shift = Column(Boolean, default=False)
    next_checkin_due = Column(DateTime, nullable=True)  # When next check-in is required
    missed_checkin = Column(Boolean, default=False)  # True if check-in was missed
    alert_sent = Column(Boolean, default=False)  # True if alert was sent for missed check-in
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class SafeZone(Base):
    """Safe zones (police stations, 24hr shops, well-lit areas)."""
    __tablename__ = "safe_zones"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_type = Column(String, nullable=False)  # police_station, shop_24hr, well_lit_area
    name = Column(String, nullable=False)
    location = Column(JSON, nullable=False)  # {latitude, longitude}
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_24hr = Column(Boolean, default=False)
    safety_score = Column(Float, nullable=True)  # Additional safety rating
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RideAlong(Base):
    """Ride-along tracking for friends/family."""
    __tablename__ = "ride_along"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rider_id = Column(String, nullable=False, index=True)
    route_id = Column(String, nullable=True, index=True)
    delivery_id = Column(String, nullable=True, index=True)
    tracker_name = Column(String, nullable=False)  # Name of person tracking
    tracker_phone = Column(String, nullable=True)
    tracker_email = Column(String, nullable=True)
    share_token = Column(String, unique=True, nullable=False)  # Unique token for sharing
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)  # When tracking expires
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, nullable=True)


class User(Base):
    """User model for authentication and profile info."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="rider")  # delivery_person, rider
    
    # Common Profile Info
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Delivery Person Specific
    license_number = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    
    # Rider Specific
    gender = Column(String, nullable=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
