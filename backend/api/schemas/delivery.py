"""Pydantic schemas for delivery endpoints."""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class DeliveryPriority(str, Enum):
    """Delivery priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DeliveryStatus(str, Enum):
    """Delivery status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Coordinate(BaseModel):
    """Geographic coordinate."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


class DeliveryStop(BaseModel):
    """Single delivery stop."""
    stop_id: str = Field(..., description="Unique stop identifier")
    address: str = Field(..., description="Delivery address")
    coordinates: Coordinate = Field(..., description="Stop coordinates")
    priority: DeliveryPriority = Field(DeliveryPriority.MEDIUM, description="Delivery priority")
    time_window_start: Optional[datetime] = Field(None, description="Earliest delivery time")
    time_window_end: Optional[datetime] = Field(None, description="Latest delivery time")
    package_weight: Optional[float] = Field(1.0, ge=0, description="Package weight in kg")
    special_instructions: Optional[str] = Field(None, description="Special delivery instructions")

    class Config:
        json_schema_extra = {
            "example": {
                "stop_id": "STOP001",
                "address": "123 Main St, New York, NY",
                "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
                "priority": "high",
                "package_weight": 2.5,
                "special_instructions": "Ring twice"
            }
        }


class RouteOptimizationRequest(BaseModel):
    """Request for route optimization."""
    starting_point: Coordinate = Field(..., description="Starting location")
    stops: List[DeliveryStop] = Field(..., min_items=1, description="List of delivery stops")
    optimize_for: List[str] = Field(
        ["time", "distance", "fuel", "safety"],
        description="Optimization objectives"
    )
    rider_info: Optional[Dict] = Field(
        {"gender": "neutral", "prefers_safe_routes": True},
        description="Rider information for safety optimization"
    )
    vehicle_type: str = Field("motorcycle", description="Vehicle type")
    avoid_highways: bool = Field(False, description="Avoid highways")
    avoid_tolls: bool = Field(False, description="Avoid tolls")
    departure_time: Optional[datetime] = Field(None, description="Departure time")

    @validator('stops')
    def validate_stops(cls, v):
        if len(v) > 50:
            raise ValueError("Maximum 50 stops allowed")
        return v


class RouteSegment(BaseModel):
    """Route segment between two points."""
    from_stop: str = Field(..., description="Starting stop ID")
    to_stop: str = Field(..., description="Destination stop ID")
    distance_meters: float = Field(..., ge=0, description="Distance in meters")
    duration_seconds: float = Field(..., ge=0, description="Duration in seconds")
    safety_score: float = Field(..., ge=0, le=100, description="Safety score (0-100)")
    estimated_fuel_liters: float = Field(..., ge=0, description="Estimated fuel consumption")


class OptimizedRoute(BaseModel):
    """Optimized delivery route."""
    route_id: str = Field(..., description="Unique route identifier")
    total_distance_meters: float = Field(..., ge=0, description="Total distance")
    total_duration_seconds: float = Field(..., ge=0, description="Total duration")
    average_safety_score: float = Field(..., ge=0, le=100, description="Average safety score")
    total_fuel_liters: float = Field(..., ge=0, description="Total fuel consumption")
    sequence: List[str] = Field(..., description="Stop sequence")
    segments: List[RouteSegment] = Field(..., description="Route segments")
    optimizations_applied: List[str] = Field(..., description="Optimizations applied")
    created_at: datetime = Field(default_factory=datetime.now)
    estimated_arrivals: Dict[str, datetime] = Field(..., description="Estimated arrival times")

    class Config:
        json_schema_extra = {
            "example": {
                "route_id": "ROUTE_123",
                "total_distance_meters": 15000,
                "total_duration_seconds": 3600,
                "average_safety_score": 85.5,
                "total_fuel_liters": 1.275,
                "sequence": ["STOP001", "STOP002", "STOP003"]
            }
        }


class RouteUpdateRequest(BaseModel):
    """Request to update an existing route."""
    action: str = Field(..., description="Action: add_stop, remove_stop, reorder")
    stop_id: Optional[str] = Field(None, description="Stop ID (for add/remove)")
    new_stop: Optional[DeliveryStop] = Field(None, description="New stop to add")
    new_sequence: Optional[List[str]] = Field(None, description="New stop sequence")


class RouteResponse(BaseModel):
    """Response for route operations."""
    success: bool
    message: str
    data: Optional[OptimizedRoute] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Route optimized successfully",
                "data": {}
            }
        }

