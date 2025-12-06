"""Safety endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.safety import (
    SafetyScoreRequest,
    SafetyScoreResponse,
    LocationSafetyScore,
    SafetyFactor,
    HeatmapRequest,
    SafetyHeatmapResponse,
    SafetyConditionsRequest,
    SafetyConditionsResponse
)
from api.schemas.delivery import Coordinate
from api.models.safety_scorer import SafetyScorer
from api.services.database import DatabaseService
from api.services.safety import SafetyService
from database.database import get_db
from loguru import logger

router = APIRouter()
safety_scorer = SafetyScorer()
safety_service = SafetyService()


@router.post("/safety/score", response_model=SafetyScoreResponse)
async def calculate_safety_score(
    request: SafetyScoreRequest,
    db: Session = Depends(get_db)
):
    """Calculate safety score for a route."""
    try:
        logger.info(f"Calculating safety score for route with {len(request.coordinates)} points")
        
        # Score the route
        rider_info = {"gender": request.rider_gender}
        safety_data = safety_scorer.score_route(
            coordinates=request.coordinates,
            time_of_day=request.time_of_day,
            rider_info=rider_info
        )
        
        # Build segment scores
        segment_scores = []
        for segment in safety_data["segment_scores"]:
            if request.include_factors:
                factors = [
                    SafetyFactor(**factor)
                    for factor in segment["factors"]
                ]
            else:
                factors = []
            
            segment_scores.append(
                LocationSafetyScore(
                    coordinates=segment["coordinates"],
                    overall_score=segment["overall_score"],
                    factors=factors,
                    risk_level=segment.get("risk_level", "medium"),
                    recommendations=[]
                )
            )
        
        return SafetyScoreResponse(
            route_safety_score=safety_data["route_safety_score"],
            average_score=safety_data["average_score"],
            segment_scores=segment_scores,
            improvement_suggestions=safety_data.get("improvement_suggestions", [])
        )
    
    except Exception as e:
        logger.error(f"Error calculating safety score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/safety/heatmap", response_model=SafetyHeatmapResponse)
async def get_safety_heatmap(request: HeatmapRequest):
    """Get safety heatmap for a geographic region."""
    try:
        logger.info("Generating safety heatmap")
        
        # In production, this would fetch real safety data
        # For now, generate sample heatmap points
        bbox = request.bounding_box
        resolution = request.resolution
        
        heatmap_points = []
        
        # Generate grid points
        lat_step = (bbox.get("max_lat", 41) - bbox.get("min_lat", 40)) / resolution
        lon_step = (bbox.get("max_lon", -73) - bbox.get("min_lon", -74)) / resolution
        
        for i in range(resolution):
            for j in range(resolution):
                lat = bbox.get("min_lat", 40) + i * lat_step
                lon = bbox.get("min_lon", -74) + j * lon_step
                
                from api.schemas.delivery import Coordinate
                coord = Coordinate(latitude=lat, longitude=lon)
                
                # Get safety score
                segment_data = safety_scorer.score_route(
                    coordinates=[coord],
                    time_of_day=request.time_of_day
                )
                score = segment_data["route_safety_score"]
                
                # Mock density
                import random
                density = random.randint(0, 10)
                
                from api.schemas.safety import HeatmapPoint
                heatmap_points.append(
                    HeatmapPoint(
                        coordinates=coord,
                        safety_score=score,
                        density=density
                    )
                )
        
        scores = [p.safety_score for p in heatmap_points]
        
        return SafetyHeatmapResponse(
            heatmap_points=heatmap_points,
            min_score=min(scores),
            max_score=max(scores),
            average_score=sum(scores) / len(scores)
        )
    
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/safety/conditions/{location}", response_model=SafetyConditionsResponse)
async def get_safety_conditions(location: str, request: SafetyConditionsRequest):
    """Get safety conditions at a specific location."""
    try:
        logger.info(f"Getting safety conditions for location: {location}")
        
        # Score location
        rider_info = {}
        score, factors = safety_scorer.score_location(
            coord=request.location,
            time_of_day=request.time_of_day,
            rider_info=rider_info
        )
        
        # In production, would fetch real data
        # Mock additional data
        import random
        
        return SafetyConditionsResponse(
            location=request.location,
            lighting_score=score,
            patrol_density=random.uniform(40, 90),
            crime_incidents_recent=random.randint(0, 5),
            traffic_density=random.choice(["low", "medium", "high"]),
            nearby_establishments=["Police Station", "24/7 Store", "Gas Station"],
            overall_score=score,
            recommendations=safety_scorer._get_improvement_suggestions(score)
        )
    
    except Exception as e:
        logger.error(f"Error getting safety conditions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Safety Features for Women Riders

class PanicButtonRequest(BaseModel):
    """Panic button request."""
    rider_id: str = Field(..., description="Rider ID")
    location: Coordinate = Field(..., description="Current location")
    route_id: Optional[str] = Field(None, description="Current route ID")
    delivery_id: Optional[str] = Field(None, description="Current delivery ID")


class CheckInRequest(BaseModel):
    """Check-in request."""
    rider_id: str = Field(..., description="Rider ID")
    location: Coordinate = Field(..., description="Current location")
    route_id: Optional[str] = Field(None, description="Current route ID")
    delivery_id: Optional[str] = Field(None, description="Current delivery ID")
    is_night_shift: Optional[bool] = Field(None, description="Is night shift (auto-detected if not provided)")


class SafeZoneRequest(BaseModel):
    """Safe zone search request."""
    location: Coordinate = Field(..., description="Current location")
    radius_meters: int = Field(2000, description="Search radius in meters")
    zone_types: Optional[List[str]] = Field(None, description="Zone types: police_station, shop_24hr, well_lit_area")


class RideAlongRequest(BaseModel):
    """Ride-along creation request."""
    rider_id: str = Field(..., description="Rider ID")
    tracker_name: str = Field(..., description="Name of person tracking")
    tracker_phone: Optional[str] = Field(None, description="Tracker phone number")
    tracker_email: Optional[str] = Field(None, description="Tracker email")
    route_id: Optional[str] = Field(None, description="Current route ID")
    delivery_id: Optional[str] = Field(None, description="Current delivery ID")
    expires_hours: int = Field(24, description="Hours until tracking expires")


@router.post("/safety/panic-button")
async def trigger_panic_button(
    request: PanicButtonRequest,
    db: Session = Depends(get_db)
):
    """Trigger panic button - sends alerts to company and emergency contacts.
    
    This is a critical safety feature that:
    - Sends immediate alert to delivery company
    - Notifies all emergency contacts
    - Shares live location
    - Can optionally notify emergency services
    """
    try:
        alert_data = safety_service.trigger_panic_button(
            db=db,
            rider_id=request.rider_id,
            location=request.location,
            route_id=request.route_id,
            delivery_id=request.delivery_id
        )
        
        return {
            "success": True,
            "message": "Panic alert triggered successfully",
            "data": alert_data
        }
    
    except Exception as e:
        logger.error(f"Error triggering panic button: {e}")
        raise HTTPException(status_code=500, detail=f"Panic button failed: {str(e)}")


@router.post("/safety/check-in")
async def rider_check_in(
    request: CheckInRequest,
    db: Session = Depends(get_db)
):
    """Record rider check-in.
    
    For night shifts, riders must check in every 30 minutes.
    System automatically alerts if check-in is missed.
    """
    try:
        checkin_data = safety_service.check_in(
            db=db,
            rider_id=request.rider_id,
            location=request.location,
            route_id=request.route_id,
            delivery_id=request.delivery_id,
            is_night_shift=request.is_night_shift
        )
        
        return {
            "success": True,
            "message": "Check-in recorded successfully",
            "data": checkin_data
        }
    
    except Exception as e:
        logger.error(f"Error recording check-in: {e}")
        raise HTTPException(status_code=500, detail=f"Check-in failed: {str(e)}")


@router.post("/safety/safe-zones")
async def get_safe_zones(
    request: SafeZoneRequest,
    db: Session = Depends(get_db)
):
    """Get nearby safe zones (police stations, 24hr shops, well-lit areas).
    
    Returns locations of:
    - Police stations
    - 24-hour convenience stores/shops
    - Well-lit public areas
    """
    try:
        safe_zones = safety_service.get_safe_zones(
            location=request.location,
            radius_meters=request.radius_meters,
            zone_types=request.zone_types
        )
        
        return {
            "success": True,
            "message": f"Found {len(safe_zones)} safe zones",
            "data": {
                "safe_zones": safe_zones,
                "location": {
                    "latitude": request.location.latitude,
                    "longitude": request.location.longitude
                },
                "radius_meters": request.radius_meters
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting safe zones: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get safe zones: {str(e)}")


@router.post("/safety/ride-along")
async def create_ride_along(
    request: RideAlongRequest,
    db: Session = Depends(get_db)
):
    """Create ride-along tracking link for friends/family.
    
    Allows friends or family to track rider in real-time during deliveries.
    Returns a shareable token/URL for tracking.
    """
    try:
        ride_along_data = safety_service.create_ride_along(
            db=db,
            rider_id=request.rider_id,
            tracker_name=request.tracker_name,
            tracker_phone=request.tracker_phone,
            tracker_email=request.tracker_email,
            route_id=request.route_id,
            delivery_id=request.delivery_id,
            expires_hours=request.expires_hours
        )
        
        return {
            "success": True,
            "message": "Ride-along tracking created successfully",
            "data": ride_along_data
        }
    
    except Exception as e:
        logger.error(f"Error creating ride-along: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create ride-along: {str(e)}")


@router.get("/safety/ride-along/{share_token}")
async def get_ride_along_status(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Get current rider location for ride-along tracking.
    
    Used by friends/family to track rider location in real-time.
    """
    try:
        status = safety_service.get_ride_along_status(
            db=db,
            share_token=share_token
        )
        
        if not status:
            raise HTTPException(status_code=404, detail="Ride-along not found or expired")
        
        return {
            "success": True,
            "message": "Ride-along status retrieved",
            "data": status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ride-along status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ride-along status: {str(e)}")

