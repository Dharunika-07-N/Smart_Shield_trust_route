"""Traffic data endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import Coordinate
from api.schemas.traffic import (
    TrafficSegmentResponse,
    TrafficRouteResponse,
    RouteSegmentTraffic
)
from api.services.traffic import TrafficService
from database.database import get_db
from loguru import logger

router = APIRouter()
traffic_service = TrafficService()


@router.post("/traffic/segment", response_model=TrafficSegmentResponse)
async def get_traffic_for_segment(
    start: Coordinate,
    end: Coordinate,
    db: Session = Depends(get_db)
):
    """Get traffic level for a route segment.
    
    Returns traffic level: low, medium, high
    """
    try:
        traffic_level, dist, duration = traffic_service.get_traffic_level(start, end)
        speed = dist / duration if duration > 0 else 0
        congestion = traffic_service.calculate_congestion_percentage(traffic_level)
        
        return TrafficSegmentResponse(
            traffic_level=traffic_level,
            distance_meters=dist,
            estimated_duration_seconds=duration,
            average_speed_ms=speed,
            congestion_percentage=congestion
        )
    
    except Exception as e:
        logger.error(f"Error getting traffic data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traffic/route", response_model=TrafficRouteResponse)
async def get_traffic_for_route(
    coordinates: List[Coordinate],
    db: Session = Depends(get_db)
):
    """Get traffic data for entire route with multiple segments."""
    try:
        if len(coordinates) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 coordinates")
        
        # Get traffic data for all segments
        route_segments = traffic_service.get_route_traffic(coordinates)
        
        # Build response segments
        response_segments = [
            RouteSegmentTraffic(
                start=seg["start"],
                end=seg["end"],
                traffic_level=seg["traffic_level"],
                distance_meters=seg["distance_meters"],
                duration_seconds=seg["duration_seconds"]
            )
            for seg in route_segments
        ]
        
        # Optimize and get summary
        optimization = traffic_service.optimize_for_traffic(route_segments)
        
        return TrafficRouteResponse(
            segments=response_segments,
            total_distance_meters=optimization["total_distance_meters"],
            total_duration_seconds=optimization["total_duration_seconds"],
            average_traffic=optimization["average_traffic"],
            route_summary={
                "traffic_breakdown": optimization["traffic_breakdown"],
                "efficiency_score": optimization["route_efficiency_score"]
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting route traffic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

