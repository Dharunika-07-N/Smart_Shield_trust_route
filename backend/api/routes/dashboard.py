"""Dashboard API endpoints for stats and analytics."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, Route, SafetyFeedback, DeliveryStatus
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from loguru import logger
import random

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    user_id: int = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics for the rider."""
    try:
        # Calculate stats from database
        total_deliveries = db.query(DeliveryStatus).count()
        
        # Safety score calculation (average from feedback)
        safety_feedbacks = db.query(SafetyFeedback).all()
        avg_safety = 87 if not safety_feedbacks else sum(f.safety_rating for f in safety_feedbacks if hasattr(f, 'safety_rating')) / max(len(safety_feedbacks), 1)
        
        # Mock fuel savings (would be calculated from route efficiency)
        fuel_saved = round(24.5 + random.uniform(-2, 2), 1)
        
        # Average delivery time
        avg_time = 18
        
        return {
            "status": "success",
            "data": {
                "active_deliveries": {
                    "value": "12",
                    "subValue": "4 in transit",
                    "trend": "+8% vs last week"
                },
                "safety_score": {
                    "value": f"{int(avg_safety)}%",
                    "subValue": "Above average",
                    "trend": "+5% vs last week"
                },
                "fuel_saved": {
                    "value": f"{fuel_saved}L",
                    "subValue": "This week",
                    "trend": "+12% vs last week"
                },
                "avg_delivery_time": {
                    "value": f"{avg_time} min",
                    "subValue": "Target: 20 min",
                    "trend": "+3% vs last week"
                }
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deliveries/queue")
async def get_delivery_queue(
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current delivery queue with details."""
    try:
        # Mock delivery queue data (would come from actual delivery system)
        deliveries = [
            {
                "id": "#DEL-2847",
                "customer_name": "Rajesh Sharma",
                "address": "42, Anna Nagar East, Chennai 600102",
                "estimated_time": "12 mins",
                "distance": "3.2 km",
                "safety_score": 88,
                "status": "In Transit",
                "priority": "High",
                "priority_color": "amber"
            },
            {
                "id": "#DEL-2848",
                "customer_name": "Lakshmi Venkat",
                "address": "15/3, T. Nagar Main Road, Chennai 600017",
                "estimated_time": "25 mins",
                "distance": "5.8 km",
                "safety_score": 72,
                "status": "Pending",
                "priority": "Normal",
                "priority_color": "blue"
            },
            {
                "id": "#DEL-2849",
                "customer_name": "Amit Singh",
                "address": "8, Adyar Bridge Road, Chennai 600020",
                "estimated_time": "40 mins",
                "distance": "8.4 km",
                "safety_score": 91,
                "status": "Pending",
                "priority": "Urgent",
                "priority_color": "red"
            },
            {
                "id": "#DEL-2850",
                "customer_name": "Priya Krishnan",
                "address": "23, Velachery Main Road, Chennai 600042",
                "estimated_time": "55 mins",
                "distance": "11.2 km",
                "safety_score": 85,
                "status": "Scheduled",
                "priority": "Normal",
                "priority_color": "blue"
            }
        ]
        
        return {
            "status": "success",
            "data": deliveries[:limit],
            "total": len(deliveries)
        }
    except Exception as e:
        logger.error(f"Error fetching delivery queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/zones/safety")
async def get_zone_safety(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get safety information for different zones."""
    try:
        zones = [
            {
                "name": "T. Nagar",
                "incidents": "12 incidents",
                "trend": "down",
                "score": 72,
                "color": "amber",
                "last_updated": datetime.now().isoformat()
            },
            {
                "name": "Anna Nagar",
                "incidents": "3 incidents",
                "trend": "neutral",
                "score": 88,
                "color": "green",
                "last_updated": datetime.now().isoformat()
            },
            {
                "name": "Velachery",
                "incidents": "28 incidents",
                "trend": "up",
                "score": 45,
                "color": "red",
                "last_updated": datetime.now().isoformat()
            },
            {
                "name": "Adyar",
                "incidents": "2 incidents",
                "trend": "down",
                "score": 91,
                "color": "green",
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        return {
            "status": "success",
            "data": zones,
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching zone safety: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather")
async def get_weather_conditions(
    lat: float = 13.0827,
    lon: float = 80.2707
) -> Dict[str, Any]:
    """Get current weather conditions for location."""
    try:
        # Mock weather data (would integrate with weather API)
        weather = {
            "temperature": 28,
            "condition": "Partly Cloudy",
            "icon": "☁️",
            "humidity": 72,
            "wind_speed": 12,
            "visibility": "Good",
            "impact": "Low",
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "data": weather
        }
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class OptimizeRequest(BaseModel):
    delivery_ids: List[str]

@router.post("/route/optimize")
async def optimize_current_route(
    request: OptimizeRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Optimize route for given deliveries."""
    try:
        # This would call the actual route optimization service
        return {
            "status": "success",
            "message": "Route optimization started",
            "estimated_time_saved": "8 minutes",
            "fuel_saved": "1.2L"
        }
    except Exception as e:
        logger.error(f"Error optimizing route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/recent")
async def get_recent_alerts(
    limit: int = 5,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get recent safety alerts."""
    try:
        alerts = db.query(SafetyFeedback).order_by(
            SafetyFeedback.created_at.desc()
        ).limit(limit).all()
        
        alert_data = []
        for alert in alerts:
            alert_data.append({
                "id": alert.id,
                "type": getattr(alert, 'alert_type', 'general'),
                "message": getattr(alert, 'message', 'Safety alert'),
                "location": getattr(alert, 'location', {}),
                "severity": getattr(alert, 'severity', 'medium'),
                "created_at": alert.created_at.isoformat() if alert.created_at else None
            })
        
        return {
            "status": "success",
            "data": alert_data,
            "count": len(alert_data)
        }
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
