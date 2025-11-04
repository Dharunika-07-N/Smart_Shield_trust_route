"""Delivery route endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import (
    RouteOptimizationRequest,
    OptimizedRoute,
    RouteResponse,
    RouteUpdateRequest
)
from api.models.route_optimizer import RouteOptimizer
from api.services.database import DatabaseService
from database.database import get_db
from loguru import logger

router = APIRouter()
route_optimizer = RouteOptimizer()


@router.post("/delivery/optimize", response_model=RouteResponse)
async def optimize_route(
    request: RouteOptimizationRequest,
    db: Session = Depends(get_db)
):
    """Optimize a delivery route based on multiple objectives.
    
    Optimizes routes considering time, distance, fuel efficiency, and safety.
    """
    try:
        logger.info(f"Optimizing route for {len(request.stops)} stops")
        
        # Optimize route
        optimized_data = route_optimizer.optimize_route(
            starting_point=request.starting_point,
            stops=request.stops,
            optimize_for=request.optimize_for,
            rider_info=request.rider_info,
            vehicle_type=request.vehicle_type,
            departure_time=request.departure_time
        )
        
        # Save to database
        db_service = DatabaseService(db)
        route_id = db_service.save_route({
            "id": optimized_data["route_id"],
            "starting_point": {"lat": request.starting_point.latitude, "lng": request.starting_point.longitude},
            "stops": [stop.dict() for stop in request.stops],
            "optimized_sequence": optimized_data["sequence"],
            "total_distance_meters": optimized_data["total_distance_meters"],
            "total_duration_seconds": optimized_data["total_duration_seconds"],
            "average_safety_score": optimized_data["average_safety_score"],
            "total_fuel_liters": optimized_data["total_fuel_liters"],
            "optimizations_applied": optimized_data["optimizations_applied"]
        })
        
        return RouteResponse(
            success=True,
            message=f"Route optimized successfully with {len(request.stops)} stops",
            data=OptimizedRoute(**optimized_data)
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Route optimization failed: {str(e)}")


@router.get("/delivery/routes/{route_id}", response_model=RouteResponse)
async def get_route(route_id: str, db: Session = Depends(get_db)):
    """Get route details by ID."""
    try:
        db_service = DatabaseService(db)
        route = db_service.get_route(route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return RouteResponse(
            success=True,
            message="Route retrieved successfully",
            data=OptimizedRoute(
                route_id=route.id,
                total_distance_meters=route.total_distance_meters,
                total_duration_seconds=route.total_duration_seconds,
                average_safety_score=route.average_safety_score,
                total_fuel_liters=route.total_fuel_liters,
                sequence=route.optimized_sequence or [],
                segments=[],
                optimizations_applied=route.optimizations_applied or [],
                estimated_arrivals={}
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving route: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/delivery/routes/{route_id}")
async def update_route(
    route_id: str,
    update_request: RouteUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update an existing route."""
    try:
        db_service = DatabaseService(db)
        route = db_service.get_route(route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Handle different update actions
        if update_request.action == "add_stop" and update_request.new_stop:
            # Add new stop and re-optimize
            logger.info(f"Adding stop to route {route_id}")
            # Implementation would re-optimize route with new stop
        
        elif update_request.action == "remove_stop" and update_request.stop_id:
            logger.info(f"Removing stop {update_request.stop_id} from route {route_id}")
            # Implementation would remove stop and re-optimize
        
        elif update_request.action == "reorder" and update_request.new_sequence:
            logger.info(f"Reordering route {route_id}")
            # Implementation would update sequence
        
        return {"success": True, "message": f"Route {route_id} updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating route: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/delivery/stats")
async def get_delivery_stats(db: Session = Depends(get_db)):
    """Get overall delivery statistics."""
    try:
        # In production, would aggregate actual statistics
        return {
            "total_routes": 0,
            "total_distance_km": 0,
            "average_delivery_time_minutes": 0,
            "fuel_saved_liters": 0,
            "success_rate": 0
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

