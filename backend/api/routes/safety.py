"""Safety endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
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
    SafetyConditionsRequest,
    SafetyConditionsResponse,
    PanicButtonRequest,
    PanicButtonResponse,
    PanicButtonResolveRequest,
    CheckInRequest,
    CheckInResponse,
    SafeZonesRequest,
    RideAlongRequest,
    RideAlongResponse,
    BuddyRequest
)
from api.schemas.delivery import Coordinate
from api.models.safety_scorer import SafetyScorer
from api.services.safety import SafetyService
from api.services.crime_data import CrimeDataService
from database.database import get_db
from loguru import logger

router = APIRouter()
safety_scorer = SafetyScorer()
safety_service = SafetyService()
crime_data_service = CrimeDataService()

@router.post("/safety/score", response_model=SafetyScoreResponse)
async def calculate_safety_score(
    request: SafetyScoreRequest,
    db: Session = Depends(get_db)
):
    try:
        rider_info = {"gender": request.rider_gender}
        safety_data = safety_scorer.score_route(
            coordinates=request.coordinates,
            time_of_day=request.time_of_day,
            rider_info=rider_info
        )
        return SafetyScoreResponse(
            route_safety_score=safety_data["route_safety_score"],
            average_score=safety_data["average_score"],
            segment_scores=[],
            improvement_suggestions=[]
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/safety/heatmap")
async def get_safety_heatmap(
    min_lat: float, 
    min_lng: float, 
    max_lat: float, 
    max_lng: float,
    grid_size: Optional[int] = 15
):
    """Get safety heatmap points for a bounding box."""
    try:
        bbox = {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lng,
            "max_lon": max_lng
        }
        heatmap_points = crime_data_service.get_heatmap_data(bbox, resolution=grid_size)
        return {"points": heatmap_points}
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        return {"points": [], "error": str(e)}


@router.post("/safety/panic-button", response_model=PanicButtonResponse)
async def trigger_panic_button(
    request: PanicButtonRequest,
    db: Session = Depends(get_db)
):
    """Trigger emergency SOS alert."""
    try:
        result = await safety_service.trigger_panic_button(
            db=db,
            rider_id=request.rider_id,
            location=request.location,
            route_id=request.route_id,
            delivery_id=request.delivery_id
        )
        return PanicButtonResponse(**result)
    except Exception as e:
        logger.error(f"Error triggering panic button: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/safety/panic-button/resolve")
async def resolve_panic_button(
    request: PanicButtonResolveRequest,
    db: Session = Depends(get_db)
):
    """Resolve an active emergency SOS alert."""
    try:
        return safety_service.resolve_panic_button(
            db=db,
            alert_id=request.alert_id,
            rider_id=request.rider_id,
            resolution_notes=request.resolution_notes
        )
    except Exception as e:
        logger.error(f"Error resolving panic button: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/safety/check-in", response_model=CheckInResponse)
async def rider_check_in(
    request: CheckInRequest,
    db: Session = Depends(get_db)
):
    """Record rider check-in."""
    try:
        result = safety_service.check_in(
            db=db,
            rider_id=request.rider_id,
            location=request.location,
            route_id=request.route_id,
            delivery_id=request.delivery_id,
            is_night_shift=request.is_night_shift
        )
        return CheckInResponse(**result)
    except Exception as e:
        logger.error(f"Error during check-in: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/safety/safe-zones", response_model=List[Dict])
async def get_safe_zones(
    request: SafeZonesRequest
):
    """Get nearby safe zones."""
    try:
        return safety_service.get_safe_zones(
            location=request.location,
            radius_meters=request.radius_meters,
            zone_types=request.zone_types
        )
    except Exception as e:
        logger.error(f"Error getting safe zones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/safety/ride-along", response_model=RideAlongResponse)
async def create_ride_along(
    request: RideAlongRequest,
    db: Session = Depends(get_db)
):
    """Create a ride-along tracking link."""
    try:
        result = safety_service.create_ride_along(
            db=db,
            rider_id=request.rider_id,
            tracker_name=request.tracker_name,
            tracker_phone=request.tracker_phone,
            tracker_email=request.tracker_email,
            route_id=request.route_id,
            delivery_id=request.delivery_id,
            expires_hours=request.expires_hours
        )
        return RideAlongResponse(**result)
    except Exception as e:
        logger.error(f"Error creating ride-along: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/safety/ride-along/{share_token}")
async def get_ride_along_status(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Get ride-along tracking status."""
    result = safety_service.get_ride_along_status(db, share_token)
    if not result:
        raise HTTPException(status_code=404, detail="Ride-along link invalid or expired")
    return result

@router.post("/safety/buddy-request")
async def request_buddy(
    request: BuddyRequest,
    db: Session = Depends(get_db)
):
    """Request a buddy for a shift."""
    return safety_service.request_buddy(db, request.rider_id, request.route_id)

@router.get("/safety/buddy-status/{rider_id}")
async def get_buddy_status(
    rider_id: str,
    db: Session = Depends(get_db)
):
    """Get current buddy pair status."""
    result = safety_service.get_buddy_pair(db, rider_id)
    if not result:
        return {"status": "none"}
    return result

@router.get("/safety/alerts", response_model=List[Dict])
async def get_safety_alerts(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve all safety alerts (Panic/SOS)."""
    return safety_service.get_all_panic_alerts(db, limit)
