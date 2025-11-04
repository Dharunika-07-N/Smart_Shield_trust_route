"""Pydantic schemas for feedback endpoints."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from api.schemas.delivery import Coordinate


class SafetyFeedback(BaseModel):
    """Feedback on route safety."""
    route_id: str = Field(..., description="Route ID")
    rider_id: Optional[str] = Field(None, description="Rider identifier")
    feedback_type: str = Field(..., description="Type: safety, ease, accuracy")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    location: Optional[Coordinate] = Field(None, description="Location of feedback")
    comments: Optional[str] = Field(None, description="Additional comments")
    incident_type: Optional[str] = Field(None, description="Type of incident if any")
    time_of_day: str = Field("day", description="Time: day, evening, night")
    date_submitted: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "route_id": "ROUTE_123",
                "rider_id": "RIDER_456",
                "feedback_type": "safety",
                "rating": 4,
                "comments": "Well-lit route, felt safe",
                "time_of_day": "night"
            }
        }


class RouteFeedback(BaseModel):
    """Overall route feedback."""
    route_id: str
    overall_rating: float = Field(..., ge=1, le=5)
    delivery_time_accurate: bool
    navigation_clear: bool
    safety_concerns: List[str] = Field(default_factory=list)
    suggestions: Optional[str] = None


class FeedbackStats(BaseModel):
    """Feedback statistics."""
    total_feedback: int
    average_rating: float
    feedback_by_type: dict
    recent_trends: List[dict]
    safety_improvement_rate: float


class FeedbackSubmissionResponse(BaseModel):
    """Response for feedback submission."""
    success: bool
    message: str
    feedback_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Feedback submitted successfully",
                "feedback_id": "FB_789"
            }
        }

