from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database.database import get_db
from database.models import DeliveryFeedback, DeliveryRoute
from loguru import logger

router = APIRouter()

class FeedbackSubmit(BaseModel):
    route_id: str
    rider_id: str
    safety_rating: int
    route_quality_rating: int
    comfort_rating: int
    incidents_reported: List[dict] = []
    unsafe_areas: List[dict] = []
    feedback_text: Optional[str] = None

@router.post("/feedback/submit")
async def submit_feedback(feedback: FeedbackSubmit, db: Session = Depends(get_db)):
    """Submit rider feedback for a completed route."""
    try:
        # Find the internal route ID
        db_route = db.query(DeliveryRoute).filter(DeliveryRoute.route_id == feedback.route_id).first()
        if not db_route:
            # Fallback if route not in new table yet
            logger.warning(f"Route {feedback.route_id} not found in delivery_routes table")
            # In a real app, we might create a placeholder or error out
        
        new_feedback = DeliveryFeedback(
            route_id=db_route.id if db_route else None,
            rider_id=feedback.rider_id,
            safety_rating=feedback.safety_rating,
            route_quality_rating=feedback.route_quality_rating,
            comfort_rating=feedback.comfort_rating,
            incidents_reported=feedback.incidents_reported,
            unsafe_areas=feedback.unsafe_areas,
            feedback_text=feedback.feedback_text,
            submitted_at=datetime.utcnow()
        )
        
        db.add(new_feedback)
        db.commit()
        
        # After feedback is submitted, the RL agent could be updated
        # This is part of the feedback loop renovation
        
        return {"status": "success", "message": "Feedback submitted successfully"}
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
