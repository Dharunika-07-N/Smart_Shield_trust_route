"""Pydantic schemas for safety endpoints."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from api.schemas.delivery import Coordinate


class SafetyScoreRequest(BaseModel):
    """Request for safety scoring."""
    coordinates: List[Coordinate] = Field(..., min_items=2, description="Route coordinates")
    time_of_day: Optional[str] = Field("day", description="Time of day: day, evening, night")
    rider_gender: Optional[str] = Field("neutral", description="Rider gender")
    include_factors: bool = Field(True, description="Include detailed safety factors")


class SafetyFactor(BaseModel):
    """Individual safety factor."""
    factor: str = Field(..., description="Factor name")
    score: float = Field(..., ge=0, le=100, description="Score (0-100)")
    weight: float = Field(..., ge=0, le=1, description="Weight in calculation")
    description: Optional[str] = None


class LocationSafetyScore(BaseModel):
    """Safety score for a specific location."""
    coordinates: Coordinate
    overall_score: float = Field(..., ge=0, le=100, description="Overall safety score")
    factors: List[SafetyFactor] = Field(default_factory=list, description="Safety factors")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    recommendations: List[str] = Field(default_factory=list, description="Safety recommendations")


class SafetyScoreResponse(BaseModel):
    """Response for safety scoring."""
    route_safety_score: float = Field(..., ge=0, le=100, description="Overall route safety")
    average_score: float = Field(..., ge=0, le=100, description="Average safety score")
    segment_scores: List[LocationSafetyScore] = Field(..., description="Scores per segment")
    safest_alternatives: Optional[List[Coordinate]] = None
    improvement_suggestions: List[str] = Field(default_factory=list)


class HeatmapRequest(BaseModel):
    """Request for safety heatmap."""
    min_lat: float
    min_lng: float
    max_lat: float
    max_lng: float
    grid_size: Optional[int] = 10


class SafetyHeatmapResponse(BaseModel):
    """Response for safety heatmap."""
    bounds: Dict[str, float]
    points: List[Dict]


class SafetyConditionsRequest(BaseModel):
    """Request for safety conditions at location."""
    location: Coordinate
    time_of_day: Optional[str] = "day"


class SafetyConditionsResponse(BaseModel):
    """Response for safety conditions."""
    location: Coordinate
    lighting_score: float = Field(..., ge=0, le=100)
    patrol_density: float = Field(..., ge=0, description="Patrol density score")
    crime_incidents_recent: int = Field(..., ge=0)
    traffic_density: str = Field(..., description="Traffic: low, medium, high")
    nearby_establishments: List[str] = Field(default_factory=list)
    user_safety_rating: Optional[float] = Field(None, ge=0, le=5)
    overall_score: float = Field(..., ge=0, le=100)
    recommendations: List[str] = Field(default_factory=list)
