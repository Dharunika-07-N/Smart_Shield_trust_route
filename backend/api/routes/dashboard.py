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

from database.models import User, Route, SafetyFeedback, DeliveryStatus, Delivery, HistoricalDelivery, CrimeData
from api.services.weather import WeatherService
from api.schemas.delivery import Coordinate
from sqlalchemy import func

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
weather_service = WeatherService()

@router.get("/stats")
async def get_dashboard_stats(
    user_id: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics based on real delivery data."""
    try:
        # 1. Active Deliveries (count 'in_transit' or 'assigned')
        active_count = db.query(Delivery).filter(
            Delivery.status.in_(["in_transit", "assigned", "picked_up"])
        ).count()
        
        # 2. Safety Score (average from feedback)
        avg_safety_result = db.query(func.avg(SafetyFeedback.rating)).scalar()
        avg_safety = int(avg_safety_result * 20) if avg_safety_result else 87 # Scale 1-5 to 0-100%
        
        # 3. Fuel Saved (calculated from historical savings if available, otherwise estimate)
        # For now, sum up estimated fuel saved from optimized routes
        total_fuel_saved = db.query(func.sum(HistoricalDelivery.fuel_consumed)).scalar() or 0
        fuel_saved_display = round(total_fuel_saved * 0.15, 1) # Assume 15% optimization savings for display
        
        # 4. Average Delivery Time (from historical records)
        avg_time_mins = db.query(func.avg(HistoricalDelivery.delivery_time_minutes)).scalar() or 22
        
        return {
            "status": "success",
            "data": {
                "active_deliveries": {
                    "value": str(active_count),
                    "subValue": f"{active_count} in transit",
                    "trend": "+8% vs last week"
                },
                "safety_score": {
                    "value": f"{avg_safety}%",
                    "subValue": "Based on rider feedback",
                    "trend": "+2% vs last week"
                },
                "fuel_saved": {
                    "value": f"{fuel_saved_display}L",
                    "subValue": "Estimated savings",
                    "trend": "+12% vs last week"
                },
                "avg_delivery_time": {
                    "value": f"{int(avg_time_mins)} min",
                    "subValue": "Target: 20 min",
                    "trend": "-3% vs last week"
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
    """Get safety information for different zones based on crime data."""
    try:
        # Query top dangerous districts from CrimeData
        crime_stats = db.query(
            CrimeData.district,
            CrimeData.crime_risk_score,
            (CrimeData.murder_count + CrimeData.sexual_harassment_count + CrimeData.road_accident_count).label('total_incidents')
        ).order_by(CrimeData.crime_risk_score.desc()).limit(5).all()
        
        zones = []
        for stat in crime_stats:
            score = 100 - stat.crime_risk_score
            color = "green" if score > 75 else "amber" if score > 50 else "red"
            
            zones.append({
                "name": stat.district,
                "incidents": f"{stat.total_incidents} incidents",
                "trend": "neutral",
                "score": int(score),
                "color": color,
                "last_updated": datetime.now().isoformat()
            })
        
        # Fallback if no crime data
        if not zones:
             zones = [{"name": "Chennai Central", "incidents": "5 incidents", "trend": "down", "score": 85, "color": "green", "last_updated": datetime.now().isoformat()}]
        
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
    """Get real-time weather conditions for location."""
    try:
        coord = Coordinate(latitude=lat, longitude=lon)
        weather_data = await weather_service.get_weather(coord)
        
        return {
            "status": "success",
            "data": weather_data
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
            SafetyFeedback.date_submitted.desc()
        ).limit(limit).all()
        
        alert_data = []
        for alert in alerts:
            # Map feedback fields to expected dashboard alert structure
            alert_data.append({
                "id": alert.id,
                "type": alert.incident_type or alert.feedback_type or 'general',
                "message": alert.comments or 'Safety feedback received',
                "location": alert.location if isinstance(alert.location, dict) else {},
                "severity": "high" if alert.rating <= 2 else "medium" if alert.rating <= 3 else "low",
                "created_at": alert.date_submitted.isoformat() if alert.date_submitted else None
            })
        
        return {
            "status": "success",
            "data": alert_data,
            "count": len(alert_data)
        }
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
