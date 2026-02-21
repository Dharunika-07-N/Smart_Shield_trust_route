from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from api.deps import get_current_active_user
from database.models import User, DeliveryStatus
from api.services.database import DatabaseService
from api.services.route_monitor import RouteMonitor
from loguru import logger
from datetime import datetime
from typing import Dict, Set, Optional
from pydantic import BaseModel

from api.routes.notifications import manager as notification_manager
from api.services.geospatial import geo_service

router = APIRouter(prefix="/tracking", tags=["Tracking"])
route_monitor = RouteMonitor()

class LocationUpdate(BaseModel):
    delivery_id: str
    route_id: Optional[str] = None
    latitude: float
    longitude: float
    status: str = "in_transit"
    speed_kmh: Optional[float] = None
    heading: Optional[float] = None
    battery_level: Optional[int] = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
    
    async def broadcast(self, channel: str, data: dict):
        if channel in self.active_connections:
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(data)
                except:
                    pass

manager = ConnectionManager()

@router.post("/location")
async def update_location(
    update: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update live location from mobile app."""
    db_service = DatabaseService(db)
    
    location_data = {
        "delivery_id": update.delivery_id,
        "route_id": update.route_id,
        "rider_id": current_user.id,
        "current_location": {"latitude": update.latitude, "longitude": update.longitude},
        "status": update.status,
        "speed_kmh": update.speed_kmh,
        "heading": update.heading,
        "battery_level": update.battery_level,
        "timestamp": datetime.utcnow()
    }
    
    db_service.save_location_update(location_data)
    
    # Update H3 Index in the high-performance Geospatial Service
    geo_service.update_rider_location(
        rider_id=current_user.id,
        latitude=update.latitude,
        longitude=update.longitude
    )
    
    # Check for route deviation
    reoptimization_needed = False
    if update.route_id:
        from api.schemas.delivery import Coordinate
        needs_reopt, _ = route_monitor.check_deviation(
            db=db,
            route_id=update.route_id,
            rider_id=current_user.id,
            delivery_id=update.delivery_id,
            actual_location=Coordinate(latitude=update.latitude, longitude=update.longitude),
            current_time=datetime.utcnow()
        )
        reoptimization_needed = needs_reopt

    # Broadcast update
    broadcast_data = {
        "type": "location_update",
        "rider_id": current_user.id,
        "delivery_id": update.delivery_id,
        "location": location_data["current_location"],
        "status": update.status,
        "timestamp": datetime.utcnow().isoformat(),
        "reoptimization_needed": reoptimization_needed
    }
    
    await manager.broadcast(update.delivery_id, broadcast_data)
    await manager.broadcast("live_fleet", broadcast_data) # Global channel for dispatchers
    
    # Also broadcast to global system notifications
    await notification_manager.broadcast({
        "type": "rider_location_update",
        "data": broadcast_data
    })
    
    return {"success": True, "reoptimization_needed": reoptimization_needed}

@router.websocket("/live/{channel}")
async def websocket_tracking(websocket: WebSocket, channel: str):
    """WebSocket for live tracking (channel can be delivery_id or 'live_fleet')."""
    await manager.connect(websocket, channel)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
