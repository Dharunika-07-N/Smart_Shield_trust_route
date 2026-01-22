from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from database.database import Base
from datetime import datetime
import uuid
import datetime as dt


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

class Delivery(Base):
    """Core delivery/order model."""
    __tablename__ = "deliveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, unique=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    pickup_location = Column(JSON, nullable=False) # {lat, lng, address}
    dropoff_location = Column(JSON, nullable=False) # {lat, lng, address}
    status = Column(String, default="pending") # pending, assigned, picked_up, in_transit, delivered, failed
    assigned_rider_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)

class DeliveryBatch(Base):
    """Batched deliveries for optimization."""
    __tablename__ = "delivery_batches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rider_id = Column(String, ForeignKey("users.id"))
    delivery_ids = Column(JSON, nullable=False) # List of delivery IDs
    route_geometry = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DeliveryProof(Base):
    """Proof of delivery (photo, signature)."""
    __tablename__ = "delivery_proofs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    delivery_id = Column(String, ForeignKey("deliveries.id"), unique=True)
    photo_url = Column(String, nullable=True)
    signature_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    """Customer model."""
    __tablename__ = "customers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    addresses = Column(JSON, default=list)
    preferences = Column(JSON, default=dict)

class BuddyPair(Base):
    """Buddy system for night deliveries."""
    __tablename__ = "buddy_pairs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rider1_id = Column(String, ForeignKey("users.id"))
    rider2_id = Column(String, ForeignKey("users.id"))
    shift_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="matched") # matching, matched, dissolved
    route_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)




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
    role = Column(String, default="rider")  # admin, dispatcher, rider
    status = Column(String, default="active") # active, inactive, suspended
    
    # Common Profile Info
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Relationship to RiderProfile
    rider_profile = relationship("RiderProfile", back_populates="user", uselist=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RiderProfile(Base):
    """Specific profile for riders."""
    __tablename__ = "rider_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    vehicle_type = Column(String, nullable=True)
    license_number = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    preferences = Column(JSON, default=dict) # Route preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="rider_profile")

class UserSession(Base):
    """User sessions for authentication tracking."""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DeliveryRoute(Base):
    __tablename__ = "delivery_routes"
    
    id = Column(Integer, primary_key=True)
    route_id = Column(String, unique=True, index=True)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)
    
    # Route geometry storage
    route_geometry = Column(JSON, nullable=True) # List of [lat, lng]
    
    # Predictions
    predicted_time = Column(Float)  # minutes
    predicted_distance = Column(Float)  # km
    safety_score = Column(Float)  # 0-100
    
    # Actuals (filled after delivery)
    actual_time = Column(Float, nullable=True)
    actual_distance = Column(Float, nullable=True)
    delivery_success = Column(Boolean, nullable=True)
    
    # Multi-objective scores
    time_score = Column(Float)
    distance_score = Column(Float)
    fuel_score = Column(Float)
    composite_score = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    delivery_time = Column(DateTime)
    weather_conditions = Column(JSON)
    traffic_conditions = Column(JSON)
    
    # Relationships
    segments = relationship("RouteSegment", back_populates="route")
    feedback = relationship("DeliveryFeedback", back_populates="route")


class RouteSegment(Base):
    __tablename__ = "route_segments"
    
    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("delivery_routes.id"))
    segment_order = Column(Integer)
    
    # Segment geometry
    segment_geometry = Column(JSON, nullable=True) # List of [lat, lng]
    start_lat = Column(Float)
    start_lng = Column(Float)
    end_lat = Column(Float)
    end_lng = Column(Float)
    
    # Segment features
    distance = Column(Float)  # km
    duration = Column(Float)  # minutes
    safety_score = Column(Float)  # 0-100
    crime_score = Column(Float)
    accident_history = Column(Float)
    lighting_score = Column(Float)
    road_quality = Column(Float)
    traffic_density = Column(Float)
    
    # Time features
    hour_of_day = Column(Integer)
    day_of_week = Column(Integer)
    is_peak_hour = Column(Boolean)
    
    route = relationship("DeliveryRoute", back_populates="segments")


class CrimeData(Base):
    __tablename__ = "crime_data"
    
    id = Column(Integer, primary_key=True)
    district = Column(String, index=True)
    location = Column(JSON, nullable=True) # {latitude, longitude}
    
    # Crime statistics
    murder_count = Column(Integer, default=0)
    sexual_harassment_count = Column(Integer, default=0)
    road_accident_count = Column(Integer, default=0)
    theft_count = Column(Integer, default=0)
    
    # Aggregated risk score
    crime_risk_score = Column(Float)  # 0-100
    
    # Temporal data
    year = Column(Integer)
    month = Column(Integer, nullable=True)
    
    # Geographic coverage
    radius_km = Column(Float, default=5.0)  # Area of influence


class DeliveryFeedback(Base):
    __tablename__ = "delivery_feedback"
    
    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("delivery_routes.id"))
    
    # Rider feedback
    rider_id = Column(String)
    safety_rating = Column(Integer)  # 1-5
    route_quality_rating = Column(Integer)  # 1-5
    comfort_rating = Column(Integer)  # 1-5
    
    # Incident reports
    incidents_reported = Column(JSON)  # List of incidents
    unsafe_areas = Column(JSON)  # List of coordinates
    
    # Comments
    feedback_text = Column(String, nullable=True)
    
    # Metadata
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    route = relationship("DeliveryRoute", back_populates="feedback")


class HistoricalDelivery(Base):
    __tablename__ = "historical_deliveries"
    
    id = Column(Integer, primary_key=True)
    delivery_id = Column(String, unique=True, index=True)
    
    # Route info
    origin_lat = Column(Float)
    origin_lng = Column(Float)
    destination_lat = Column(Float)
    destination_lng = Column(Float)
    
    # Outcome
    delivery_time_minutes = Column(Float)
    distance_km = Column(Float)
    fuel_consumed = Column(Float, nullable=True)
    success = Column(Boolean)
    
    # Conditions
    weather = Column(JSON)
    traffic = Column(JSON)
    time_of_day = Column(Integer)
    day_of_week = Column(Integer)
    
    # Metadata
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class CrowdsourcedAlert(Base):
    __tablename__ = "crowdsourced_alerts"
    
    id = Column(Integer, primary_key=True)
    rider_id = Column(String, index=True)
    service_type = Column(String) # Swiggy, Zomato, Rapido, Red-Taxi
    location = Column(JSON) # {lat: float, lng: float}
    is_faster = Column(Boolean) # Answer to: is this route faster and less traffic
    has_traffic_issues = Column(Boolean) # Answer to: is this route has traffic issues
    created_at = Column(DateTime, default=datetime.utcnow)

