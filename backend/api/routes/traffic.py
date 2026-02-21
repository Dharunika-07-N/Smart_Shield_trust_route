"""Traffic data endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import Coordinate
from api.schemas.traffic import (
    TrafficSegmentResponse,
    TrafficRouteResponse,
    RouteSegmentTraffic
)
from api.services.traffic import TrafficService, aggregator
from database.database import get_db
from loguru import logger

router = APIRouter()
traffic_service = TrafficService()


# --- New Models for Real-time Traffic ---

class RealTimeTrafficSegment(BaseModel):
    segment_id: str
    start: Dict[str, float]
    end: Dict[str, float]
    speed_kmh: Optional[float]
    free_flow_speed: float
    traffic_level: str
    source: str
    timestamp: str

class RouteTrafficRequest(BaseModel):
    coordinates: List[List[float]] 

class RouteTrafficAnalysisResponse(BaseModel):
    overall_level: str
    overall_level_value: int
    total_segments: int
    timestamp: str
    segments: List[Dict[str, Any]]


# --- Existing Endpoints (Preserved) ---

@router.post("/traffic/segment", response_model=TrafficSegmentResponse)
async def get_traffic_for_segment(
    start: Coordinate,
    end: Coordinate,
    db: Session = Depends(get_db)
):
    """Get traffic level for a route segment."""
    try:
        traffic_level, dist, duration = await traffic_service.get_traffic_level(start, end)
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
    """Get traffic data for entire route."""
    try:
        if len(coordinates) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 coordinates")
        
        route_segments = await traffic_service.get_route_traffic(coordinates)
        
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
    except HTTPException: raise
    except Exception as e:
        logger.error(f"Error getting route traffic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- New Real-time Endpoints ---

@router.get("/traffic/segments", response_model=List[RealTimeTrafficSegment])
async def get_traffic_segments(
    min_lat: float = Query(...),
    min_lng: float = Query(...),
    max_lat: float = Query(...),
    max_lng: float = Query(...)
):
    """Get real-time traffic segments for bounding box."""
    try:
        return await traffic_service.get_bbox_traffic(min_lat, min_lng, max_lat, max_lng)
    except Exception as e:
        logger.error(f"Error fetching traffic segments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/traffic/route/analysis", response_model=RouteTrafficAnalysisResponse)
async def analyze_route_traffic(request: RouteTrafficRequest):
    """Analyze traffic for a route (list of coordinates)."""
    try:
        coords = [(c[0], c[1]) for c in request.coordinates]
        result = aggregator.get_traffic_for_route(coords)
        return RouteTrafficAnalysisResponse(
            overall_level=result['overall_level'].name,
            overall_level_value=result['overall_level'].value,
            total_segments=result['total_segments'],
            timestamp=result['timestamp'].isoformat(),
            segments=[{
                'segment_id': s.segment_id,
                'speed_kmh': s.speed_kmh,
                'traffic_level': s.traffic_level.name,
                'source': s.source
            } for s in result['segments']]
        )
    except Exception as e:
        logger.error(f"Error analyzing route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traffic/status")
async def get_traffic_status():
    """Get status of traffic providers."""
    providers = []
    for p, provider in aggregator.providers:
        providers.append({
            'name': provider.__class__.__name__,
            'priority': p,
            'type': 'real-time' if 'OpenTraffic' in provider.__class__.__name__ else 'estimated'
        })
    return {'status': 'operational', 'providers': providers}

@router.get("/traffic/levels")
async def get_traffic_levels():
    """Get traffic level definitions."""
    return {'levels': [
        {'value': 0, 'name': 'UNKNOWN', 'color': '#9ca3af'},
        {'value': 1, 'name': 'FREE_FLOW', 'color': '#10b981'},
        {'value': 2, 'name': 'LIGHT', 'color': '#84cc16'},
        {'value': 3, 'name': 'MODERATE', 'color': '#f59e0b'},
        {'value': 4, 'name': 'HEAVY', 'color': '#f97316'},
        {'value': 5, 'name': 'SEVERE', 'color': '#ef4444'}
    ]}
