"""Database service for API operations."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from database.database import get_db, init_db as db_init
from database.models import Route, SafetyFeedback, SafetyScore, DeliveryStatus

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
    
    def save_location_update(self, location_data: Dict[str, Any]) -> str:
        """Save delivery location update."""
        try:
            status = DeliveryStatus(**location_data)
            self.db.add(status)
            self.db.commit()
            self.db.refresh(status)
            logger.info(f"Location update saved for delivery {location_data.get('delivery_id')}")
            return status.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving location update: {e}")
            raise
    
    def get_delivery_tracking(self, delivery_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get delivery tracking data with location history."""
        try:
            # Get latest status
            latest = self.db.query(DeliveryStatus).filter(
                DeliveryStatus.delivery_id == delivery_id
            ).order_by(DeliveryStatus.timestamp.desc()).first()
            
            if not latest:
                return {
                    "delivery_id": delivery_id,
                    "current_location": None,
                    "status": "pending",
                    "location_history": []
                }
            
            # Get location history
            history = self.db.query(DeliveryStatus).filter(
                DeliveryStatus.delivery_id == delivery_id
            ).order_by(DeliveryStatus.timestamp.desc()).limit(limit).all()
            
            return {
                "delivery_id": delivery_id,
                "current_location": latest.current_location,
                "status": latest.status,
                "timestamp": latest.timestamp.isoformat(),
                "speed_kmh": latest.speed_kmh,
                "heading": latest.heading,
                "battery_level": latest.battery_level,
                "location_history": [
                    {
                        "location": h.current_location,
                        "timestamp": h.timestamp.isoformat(),
                        "status": h.status,
                        "speed_kmh": h.speed_kmh,
                        "heading": h.heading
                    }
                    for h in history
                ]
            }
        except Exception as e:
            logger.error(f"Error getting delivery tracking: {e}")
            raise
    
    def get_latest_location(self, delivery_id: str) -> Optional[DeliveryStatus]:
        """Get latest location update for a delivery."""
        return self.db.query(DeliveryStatus).filter(
            DeliveryStatus.delivery_id == delivery_id
        ).order_by(DeliveryStatus.timestamp.desc()).first()

def init_db():
    """Initialize database."""
    return db_init()

