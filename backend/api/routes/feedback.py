"""Feedback endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.feedback import (
    SafetyFeedback,
    FeedbackSubmissionResponse,
    FeedbackStats,
    RouteFeedback
)
from api.services.database import DatabaseService
from database.database import get_db
from loguru import logger

router = APIRouter()


@router.post("/feedback/submit", response_model=FeedbackSubmissionResponse)
async def submit_feedback(
    feedback: SafetyFeedback,
    db: Session = Depends(get_db)
):
    """Submit rider feedback on route safety."""
    try:
        logger.info(f"Received feedback for route {feedback.route_id}")
        
        db_service = DatabaseService(db)
        
        # Save feedback
        feedback_data = feedback.dict()
        feedback_data["route_id"] = feedback.route_id
        feedback_data["rider_id"] = feedback.rider_id
        feedback_data["feedback_type"] = feedback.feedback_type
        feedback_data["rating"] = feedback.rating
        feedback_data["comments"] = feedback.comments
        feedback_data["time_of_day"] = feedback.time_of_day
        feedback_data["date_submitted"] = feedback.date_submitted
        
        if feedback.location:
            feedback_data["location"] = {
                "lat": feedback.location.latitude,
                "lng": feedback.location.longitude
            }
        
        feedback_id = db_service.save_feedback(feedback_data)
        
        # If we have enough samples, trigger model retraining
        # (implementation would check thresholds and retrain)
        
        return FeedbackSubmissionResponse(
            success=True,
            message="Feedback submitted successfully",
            feedback_id=feedback_id
        )
    
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/route")
async def submit_route_feedback(
    feedback: RouteFeedback,
    db: Session = Depends(get_db)
):
    """Submit overall route feedback."""
    try:
        logger.info(f"Received route feedback for {feedback.route_id}")
        
        # In production, would save more detailed route feedback
        return {
            "success": True,
            "message": "Route feedback submitted successfully"
        }
    
    except Exception as e:
        logger.error(f"Error submitting route feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/stats", response_model=FeedbackStats)
async def get_feedback_stats(db: Session = Depends(get_db)):
    """Get feedback statistics."""
    try:
        db_service = DatabaseService(db)
        stats = db_service.get_feedback_stats()
        
        return FeedbackStats(
            total_feedback=stats["total_feedback"],
            average_rating=stats["average_rating"],
            feedback_by_type=stats.get("feedback_by_type", {}),
            recent_trends=[],
            safety_improvement_rate=0.0
        )
    
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/route/{route_id}")
async def get_route_feedback(route_id: str, db: Session = Depends(get_db)):
    """Get feedback for a specific route."""
    try:
        # In production, would query database for route-specific feedback
        return {
            "route_id": route_id,
            "feedback_count": 0,
            "average_rating": 0,
            "feedback": []
        }
    
    except Exception as e:
        logger.error(f"Error getting route feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

