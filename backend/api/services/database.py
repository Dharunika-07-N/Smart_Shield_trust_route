"""Database service for API operations."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from database.database import get_db, init_db as db_init
from database.models import Route, SafetyFeedback, SafetyScore

class DatabaseService:
    """Service for database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_route(self, route_data: Dict[str, Any]) -> str:
        """Save optimized route to database."""
        try:
            route = Route(**route_data)
            self.db.add(route)
            self.db.commit()
            self.db.refresh(route)
            logger.info(f"Route saved with ID: {route.id}")
            return route.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving route: {e}")
            raise
    
    def get_route(self, route_id: str) -> Optional[Route]:
        """Get route by ID."""
        return self.db.query(Route).filter(Route.id == route_id).first()
    
    def save_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """Save rider feedback."""
        try:
            feedback = SafetyFeedback(**feedback_data)
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            logger.info(f"Feedback saved with ID: {feedback.id}")
            return feedback.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving feedback: {e}")
            raise
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        feedbacks = self.db.query(SafetyFeedback).all()
        if not feedbacks:
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "feedback_by_type": {}
            }
        
        return {
            "total_feedback": len(feedbacks),
            "average_rating": sum(f.rating for f in feedbacks) / len(feedbacks),
            "feedback_by_type": {}
        }
    
    def save_safety_score(self, score_data: Dict[str, Any]) -> str:
        """Save safety score."""
        try:
            score = SafetyScore(**score_data)
            self.db.add(score)
            self.db.commit()
            self.db.refresh(score)
            return score.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving safety score: {e}")
            raise

def init_db():
    """Initialize database."""
    return db_init()

