"""Safety endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
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
from api.models.safety_scorer import SafetyScorer
from api.services.database import DatabaseService
from database.database import get_db
from loguru import logger

router = APIRouter()
safety_scorer = SafetyScorer()


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

