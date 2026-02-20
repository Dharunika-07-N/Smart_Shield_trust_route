"""Delivery route endpoints."""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Dict, Set, Optional
from pydantic import BaseModel
import sys
from pathlib import Path
import json
from datetime import datetime
import asyncio

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import (
    RouteOptimizationRequest,
    OptimizedRoute,
    RouteResponse,
    RouteUpdateRequest,
    LocationUpdateRequest,
    DeliveryTrackingResponse,
    Coordinate
)
from api.models.route_optimizer import RouteOptimizer
from api.services.database import DatabaseService
from api.services.route_monitor import RouteMonitor
from database.database import get_db
from loguru import logger
from api.routes.notifications import manager as notification_manager

# Use MapsService as the primary hub (handles Google, GraphHopper, OSRM fallbacks)
from api.services.maps import MapsService
maps_service_instance = MapsService()
logger.info("Using MapsService hub for routing (Google/GraphHopper/OSRM)")

router = APIRouter()
route_optimizer = RouteOptimizer()
route_monitor = RouteMonitor()

@router.post("/optimize-route")
async def optimize_route_simple(
    origin: dict,
    destination: dict
):
    """Simple route optimization with safety scores for multiple alternatives."""
    logger.info(f"Optimize route request: origin={origin}, destination={destination}")
    
    # Get multiple route alternatives using OSRM (FREE!)
    if hasattr(maps_service_instance, 'get_directions') and asyncio.iscoroutinefunction(maps_service_instance.get_directions):
        directions = await maps_service_instance.get_directions(origin, destination, alternatives=True)
    else:
        directions = maps_service_instance.get_directions(origin, destination, alternatives=True)
    
    if not directions:
        logger.error(f"Failed to get directions for {origin} to {destination}")
        raise HTTPException(status_code=400, detail="Could not calculate routes")
    
    routes = []
    for idx, route in enumerate(directions):
        if not route.get('legs'):
            continue
            
        leg = route['legs'][0]
        
        # Calculate safety score using the route coordinates
        from api.models.safety_scorer import SafetyScorer
        safety_scorer = SafetyScorer()
        
        # Get route coordinates for safety scoring
        route_coords_list = route.get('route_coordinates', [])
        if route_coords_list:
            # Convert to Coordinate objects
            from api.schemas.delivery import Coordinate
            coords = [
                Coordinate(latitude=c['lat'], longitude=c['lng'])
                for c in route_coords_list[::max(1, len(route_coords_list)//10)]  # Sample every 10th point
            ]
            # Determine time of day
            from datetime import datetime
            hour = datetime.now().hour
            time_of_day = "day"
            if hour < 6 or hour >= 22:
                time_of_day = "night"
            elif hour < 8 or hour >= 18:
                time_of_day = "evening"
                
            safety_data = safety_scorer.score_route(coords, time_of_day=time_of_day)
            safety_score = safety_data['route_safety_score']
        else:
            safety_score = 75.0  # Default
        
        route_info = {
            'index': idx,
            'duration': leg['duration']['value'],
            'distance': leg['distance']['value'],
            'summary': route.get('summary', f'Route {idx+1}'),
            'polyline': route.get('overview_polyline', {}).get('points', ''),
            'safety_score': safety_score,
            'steps': leg.get('steps', [])
        }
        routes.append(route_info)
    
    return {'routes': routes}

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time tracking."""
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, delivery_id: str):
        """Connect a client to a delivery tracking channel."""
        await websocket.accept()
        if delivery_id not in self.active_connections:
            self.active_connections[delivery_id] = set()
        self.active_connections[delivery_id].add(websocket)
        logger.info(f"Client connected to delivery {delivery_id}. Total connections: {len(self.active_connections[delivery_id])}")
    
    def disconnect(self, websocket: WebSocket, delivery_id: str):
        """Disconnect a client from a delivery tracking channel."""
        if delivery_id in self.active_connections:
            self.active_connections[delivery_id].discard(websocket)
            if not self.active_connections[delivery_id]:
                del self.active_connections[delivery_id]
        logger.info(f"Client disconnected from delivery {delivery_id}")
    
    async def broadcast_location_update(self, delivery_id: str, data: dict):
        """Broadcast location update to all connected clients."""
        disconnected = set()
        if delivery_id in self.active_connections:
            for connection in self.active_connections[delivery_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    disconnected.add(connection)
            
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections[delivery_id].discard(conn)

    def broadcast_location_update_sync(self, delivery_id: str, data: dict):
        """Thread-safe and sync-safe broadcast for location updates."""
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    loop.create_task(self.broadcast_location_update(delivery_id, data))
                    return
            except RuntimeError:
                pass
            
            # Fallback for sync contexts
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(self.broadcast_location_update(delivery_id, data))
            new_loop.close()
        except Exception as e:
            logger.error(f"Error in sync broadcast for delivery {delivery_id}: {e}")

manager = ConnectionManager()


@router.post("/delivery/optimize", response_model=RouteResponse)
async def optimize_route(
    request: RouteOptimizationRequest,
    db: Session = Depends(get_db)
):
    """Optimize a delivery route based on multiple objectives."""
    try:
        logger.info(f"Optimizing route for {len(request.stops)} stops (Origin: {request.starting_point})")
        
        # Optimize route using the optimizer service
        optimized_data = await route_optimizer.optimize_route(
            starting_point=request.starting_point,
            stops=request.stops,
            optimize_for=request.optimize_for,
            rider_info=request.rider_info,
            vehicle_type=request.vehicle_type,
            departure_time=request.departure_time
        )
        
        # Save to database - use jsonable_encoder to handle datetime/pydantic objects
        db_service = DatabaseService(db)
        route_data_to_save = {
            "id": optimized_data["route_id"],
            "starting_point": jsonable_encoder(request.starting_point),
            "stops": jsonable_encoder(request.stops),
            "optimized_sequence": optimized_data["sequence"],
            "total_distance_meters": optimized_data["total_distance_meters"],
            "total_duration_seconds": optimized_data["total_duration_seconds"],
            "average_safety_score": optimized_data["average_safety_score"],
            "total_fuel_liters": optimized_data["total_fuel_liters"],
            "optimizations_applied": optimized_data["optimizations_applied"]
        }
        
        route_id = db_service.save_route(route_data_to_save)
        logger.info(f"Route saved to DB with ID: {route_id}")
        
        # Create response data - ensure it matches OptimizedRoute schema exactly
        response_data = OptimizedRoute(**jsonable_encoder(optimized_data))
        
        return RouteResponse(
            success=True,
            message=f"Route optimized successfully with {len(request.stops)} stops",
            data=response_data
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Optimization error: {e}")
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


@router.post("/delivery/location-update")
async def update_location(
    request: LocationUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update delivery location (called by rider app every 30 seconds).
    
    This endpoint receives GPS coordinates from the rider's device
    and broadcasts updates to all connected tracking clients via WebSocket.
    Also monitors for route deviations and triggers re-optimization if needed.
    """
    try:
        logger.info(f"Location update received for delivery {request.delivery_id}")
        
        # Save location update to database
        db_service = DatabaseService(db)
        location_data = {
            "delivery_id": request.delivery_id,
            "route_id": request.route_id,
            "rider_id": request.rider_id,
            "current_location": {
                "latitude": request.current_location.latitude,
                "longitude": request.current_location.longitude
            },
            "status": request.status.value if hasattr(request.status, 'value') else request.status,
            "speed_kmh": request.speed_kmh,
            "heading": request.heading,
            "battery_level": request.battery_level,
            "timestamp": datetime.utcnow()
        }
        
        update_id = db_service.save_location_update(location_data)
        
        # Check for route deviation if route_id is provided
        reoptimization_needed = False
        if request.route_id:
            needs_reopt, monitoring_data = route_monitor.check_deviation(
                db=db,
                route_id=request.route_id,
                rider_id=request.rider_id or "",
                delivery_id=request.delivery_id,
                actual_location=request.current_location,
                current_time=datetime.utcnow()
            )
            reoptimization_needed = needs_reopt
        
        # Prepare broadcast data
        broadcast_data = {
            "type": "location_update",
            "delivery_id": request.delivery_id,
            "timestamp": datetime.utcnow().isoformat(),
            "location": {
                "latitude": request.current_location.latitude,
                "longitude": request.current_location.longitude
            },
            "status": request.status.value if hasattr(request.status, 'value') else request.status,
            "speed_kmh": request.speed_kmh,
            "heading": request.heading,
            "battery_level": request.battery_level,
            "reoptimization_needed": reoptimization_needed
        }
        
        # Broadcast to all connected clients tracking this delivery
        await manager.broadcast_location_update(request.delivery_id, broadcast_data)
        
        # Also broadcast to global system notifications
        await notification_manager.broadcast({
            "type": "rider_location_update",
            "data": broadcast_data
        })
        
        response = {
            "success": True,
            "message": "Location updated successfully",
            "update_id": update_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if reoptimization_needed:
            response["reoptimization_needed"] = True
            response["message"] = "Location updated. Route deviation detected - reoptimization recommended."
        
        return response
    
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        raise HTTPException(status_code=500, detail=f"Location update failed: {str(e)}")


@router.get("/delivery/{delivery_id}/track", response_model=DeliveryTrackingResponse)
async def track_delivery(
    delivery_id: str,
    db: Session = Depends(get_db)
):
    """Get delivery tracking information including current location and history.
    
    This endpoint is used by customers or companies to track a delivery.
    For real-time updates, clients should connect to the WebSocket endpoint.
    """
    try:
        db_service = DatabaseService(db)
        tracking_data = db_service.get_delivery_tracking(delivery_id)
        
        return DeliveryTrackingResponse(
            success=True,
            message="Tracking data retrieved successfully",
            data=tracking_data
        )
    
    except Exception as e:
        logger.error(f"Error tracking delivery: {e}")
        raise HTTPException(status_code=500, detail=f"Tracking failed: {str(e)}")


class ReoptimizeRequest(BaseModel):
    """Request for route reoptimization."""
    current_location: Optional[Coordinate] = None
    new_stops: Optional[List[Dict]] = None


@router.post("/delivery/routes/{route_id}/reoptimize", response_model=RouteResponse)
async def reoptimize_route(
    route_id: str,
    request: Optional[ReoptimizeRequest] = None,
    db: Session = Depends(get_db)
):
    """Re-optimize route from current location.
    
    This endpoint is called when:
    - Rider deviates >500m from planned route
    - Rider takes >10min extra time
    - New deliveries are added mid-route
    
    Request Body (optional):
    {
        "current_location": {"latitude": 40.7128, "longitude": -74.0060},
        "new_stops": [
            {
                "stop_id": "STOP_NEW",
                "address": "New Address",
                "coordinates": {"latitude": 40.7210, "longitude": -74.0120},
                "priority": "medium"
            }
        ]
    }
    """
    try:
        from api.schemas.delivery import Coordinate
        from database.models import DeliveryStatus
        
        db_service = DatabaseService(db)
        route = db_service.get_route(route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Get current location from request or latest delivery status
        current_loc = None
        if request and request.current_location:
            current_loc = request.current_location
        else:
            # Try to get from latest delivery status
            latest_status = db.query(DeliveryStatus).filter(
                DeliveryStatus.route_id == route_id
            ).order_by(DeliveryStatus.timestamp.desc()).first()
            
            if latest_status:
                loc_data = latest_status.current_location
                current_loc = Coordinate(
                    latitude=loc_data.get("latitude") or loc_data.get("lat"),
                    longitude=loc_data.get("longitude") or loc_data.get("lng")
                )
        
        if not current_loc:
            raise HTTPException(
                status_code=400,
                detail="Current location required. Provide in request or ensure location updates are being sent."
            )
        
        # Get new stops from request
        new_stops = request.new_stops if request else None
        
        # Re-optimize route
        optimized_data = await route_monitor.reoptimize_route(
            db=db,
            route_id=route_id,
            current_location=current_loc,
            new_stops=new_stops
        )
        
        if not optimized_data:
            raise HTTPException(
                status_code=500,
                detail="Route reoptimization failed"
            )
        
        return RouteResponse(
            success=True,
            message="Route reoptimized successfully",
            data=OptimizedRoute(**optimized_data)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reoptimizing route: {e}")
        raise HTTPException(status_code=500, detail=f"Reoptimization failed: {str(e)}")


@router.websocket("/delivery/{delivery_id}/ws")
async def websocket_tracking(websocket: WebSocket, delivery_id: str):
    """WebSocket endpoint for real-time delivery tracking.
    
    Clients connect to this endpoint to receive live location updates.
    The server will push location updates whenever the rider sends new coordinates.
    """
    await manager.connect(websocket, delivery_id)
    
    try:
        # Send initial location if available
        db_gen = get_db()
        db = next(db_gen)
        try:
            db_service = DatabaseService(db)
            latest = db_service.get_latest_location(delivery_id)
            
            if latest:
                await websocket.send_json({
                    "type": "initial_location",
                    "delivery_id": delivery_id,
                    "location": latest.current_location,
                    "status": latest.status,
                    "timestamp": latest.timestamp.isoformat(),
                    "speed_kmh": latest.speed_kmh,
                    "heading": latest.heading
                })
        finally:
            db.close()
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for any message from client (ping/pong or other commands)
                data = await websocket.receive_text()
                # Echo back or handle client commands
                if data == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        logger.error(f"WebSocket error for delivery {delivery_id}: {e}")
    finally:
        manager.disconnect(websocket, delivery_id)

