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
    SafetyConditionsRequest,
    SafetyConditionsResponse
)
from api.schemas.delivery import Coordinate
from api.models.safety_scorer import SafetyScorer
from database.database import get_db
from loguru import logger

router = APIRouter()
safety_scorer = SafetyScorer()

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
async def get_safety_heatmap(min_lat: float, min_lng: float, max_lat: float, max_lng: float):
    return {"points": []}
