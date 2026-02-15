"""
Traffic Data API Endpoints
Provides real-time traffic information from multiple sources
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.traffic_data import get_traffic_data, get_route_traffic

router = APIRouter(prefix="/api/traffic", tags=["traffic"])


class TrafficSegmentResponse(BaseModel):
    """Traffic segment data"""
    segment_id: str
    start: dict
    end: dict
    speed_kmh: Optional[float]
    free_flow_speed: float
    traffic_level: str
    traffic_level_value: int
    timestamp: str
    source: str


class RouteTrafficRequest(BaseModel):
    """Request for route traffic information"""
    coordinates: List[List[float]]  # [[lat, lng], [lat, lng], ...]


class RouteTrafficResponse(BaseModel):
    """Traffic information for a route"""
    overall_level: str
    overall_level_value: int
    total_segments: int
    timestamp: str
    segments: List[dict]


@router.get("/segments", response_model=List[TrafficSegmentResponse])
async def get_traffic_segments(
    min_lat: float = Query(..., description="Minimum latitude"),
    min_lng: float = Query(..., description="Minimum longitude"),
    max_lat: float = Query(..., description="Maximum latitude"),
    max_lng: float = Query(..., description="Maximum longitude")
):
    """
    Get traffic data for a bounding box
    
    Returns traffic segments with speed and congestion information
    from OpenTraffic and/or OpenStreetMap estimation
    """
    try:
        bbox = (min_lat, min_lng, max_lat, max_lng)
        segments = get_traffic_data(bbox)
        return segments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching traffic data: {str(e)}")


@router.post("/route", response_model=RouteTrafficResponse)
async def get_route_traffic_info(request: RouteTrafficRequest):
    """
    Get traffic information for a specific route
    
    Analyzes traffic conditions along the provided route coordinates
    and returns overall congestion level
    """
    try:
        # Convert coordinates to tuples
        route_coords = [(coord[0], coord[1]) for coord in request.coordinates]
        
        if not route_coords:
            raise HTTPException(status_code=400, detail="Route coordinates cannot be empty")
        
        traffic_info = get_route_traffic(route_coords)
        return traffic_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing route traffic: {str(e)}")


@router.get("/status")
async def get_traffic_service_status():
    """
    Get status of traffic data providers
    
    Returns information about which traffic data sources are available
    """
    from app.services.traffic_data import default_aggregator
    
    providers_status = []
    for priority, provider in default_aggregator.providers:
        providers_status.append({
            'name': provider.__class__.__name__,
            'priority': priority,
            'type': 'real-time' if 'OpenTraffic' in provider.__class__.__name__ else 'estimated'
        })
    
    return {
        'status': 'operational',
        'providers': providers_status,
        'cache_duration_minutes': default_aggregator.cache_duration.total_seconds() / 60
    }


@router.get("/levels")
async def get_traffic_levels():
    """
    Get traffic level definitions
    
    Returns the mapping of traffic levels and their meanings
    """
    return {
        'levels': [
            {'value': 0, 'name': 'UNKNOWN', 'description': 'No traffic data available', 'color': '#9ca3af'},
            {'value': 1, 'name': 'FREE_FLOW', 'description': 'Traffic flowing freely', 'color': '#10b981'},
            {'value': 2, 'name': 'LIGHT', 'description': 'Light traffic', 'color': '#84cc16'},
            {'value': 3, 'name': 'MODERATE', 'description': 'Moderate congestion', 'color': '#f59e0b'},
            {'value': 4, 'name': 'HEAVY', 'description': 'Heavy traffic', 'color': '#f97316'},
            {'value': 5, 'name': 'SEVERE', 'description': 'Severe congestion', 'color': '#ef4444'},
        ]
    }
