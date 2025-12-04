"""Pydantic schemas for traffic endpoints."""
from pydantic import BaseModel, Field
from typing import List, Optional
from api.schemas.delivery import Coordinate


class TrafficSegmentRequest(BaseModel):
    """Request for traffic data on a segment."""
    start: Coordinate = Field(..., description="Start coordinate")
    end: Coordinate = Field(..., description="End coordinate")


class TrafficSegmentResponse(BaseModel):
    """Response for traffic segment data."""
    traffic_level: str = Field(..., description="Traffic level: low, medium, high")
    distance_meters: float = Field(..., ge=0, description="Distance in meters")
    estimated_duration_seconds: float = Field(..., ge=0, description="Estimated duration")
    average_speed_ms: float = Field(..., ge=0, description="Average speed in m/s")
    congestion_percentage: Optional[float] = Field(None, ge=0, le=100, description="Congestion percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "traffic_level": "medium",
                "distance_meters": 2500.5,
                "estimated_duration_seconds": 400.2,
                "average_speed_ms": 6.25,
                "congestion_percentage": 45.0
            }
        }


class TrafficRouteRequest(BaseModel):
    """Request for traffic data on entire route."""
    coordinates: List[Coordinate] = Field(..., min_items=2, description="Route coordinates")


class RouteSegmentTraffic(BaseModel):
    """Traffic data for a route segment."""
    start: Coordinate = Field(..., description="Start coordinate")
    end: Coordinate = Field(..., description="End coordinate")
    traffic_level: str = Field(..., description="Traffic level")
    distance_meters: float = Field(..., ge=0)
    duration_seconds: float = Field(..., ge=0)


class TrafficRouteResponse(BaseModel):
    """Response for route traffic data."""
    segments: List[RouteSegmentTraffic] = Field(..., description="Traffic data per segment")
    total_distance_meters: float = Field(..., ge=0, description="Total route distance")
    total_duration_seconds: float = Field(..., ge=0, description="Total route duration")
    average_traffic: str = Field(..., description="Average traffic level")
    route_summary: Optional[dict] = Field(None, description="Route summary statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "segments": [],
                "total_distance_meters": 12500.0,
                "total_duration_seconds": 2400.0,
                "average_traffic": "medium"
            }
        }

