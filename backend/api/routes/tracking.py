"""
Real-Time GPS Tracking Routes
=====================================
Architecture: Push-based, event-driven, cache-first

Flow:
  Rider GPS → POST /tracking/location
      → Save to DB (async)
      → Update in-memory cache (sync, O(1))
      → Broadcast via WebSocket to per-order channel
      → Broadcast to 'live_fleet' channel (dispatchers)
      → Optionally stream via SSE

Consumers:
  Customer/Dispatcher → WS /tracking/live/{delivery_id}
  Admin fleet view   → WS /tracking/live/live_fleet
  Browser SSE        → GET /tracking/stream/{delivery_id}
  Cache lookup       → GET /tracking/current/{delivery_id}

Interview keywords:
    WebSockets, SSE, real-time event streaming, Redis caching,
    push-based architecture, geo-location updates
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database.database import get_db
from api.deps import get_current_active_user
from database.models import User, DeliveryStatus
from api.services.database import DatabaseService
from api.services.route_monitor import RouteMonitor
from api.services.location_cache import location_cache
from loguru import logger
from datetime import datetime
from typing import Dict, Set, Optional, Any
from pydantic import BaseModel
import asyncio
import json

from api.routes.notifications import manager as notification_manager
from api.services.geospatial import geo_service

router = APIRouter(prefix="/tracking", tags=["Tracking"])
route_monitor = RouteMonitor()


# ─────────────────────────────────────────────────
#  Pydantic Models
# ─────────────────────────────────────────────────

class LocationUpdate(BaseModel):
    delivery_id: str
    route_id: Optional[str] = None
    latitude: float
    longitude: float
    status: str = "in_transit"
    speed_kmh: Optional[float] = None
    heading: Optional[float] = None
    battery_level: Optional[int] = None


# ─────────────────────────────────────────────────
#  WebSocket Connection Manager
#  Per-order channels → only relevant users get updates
#  "live_fleet" → global channel for dispatchers/admins
# ─────────────────────────────────────────────────

class ConnectionManager:
    """
    Manages WebSocket connections grouped by channel (order_id or 'live_fleet').
    
    This is the core of the push-based architecture:
    - Rider sends location → backend broadcasts to all watchers of that order
    - No polling, no page reloads, just smooth marker moves
    
    Why not just use a global broadcast?
    → Traffic isolation: customer of order A doesn't receive updates for order B
    → Scales horizontally (each instance manages its own connections)
    """

    def __init__(self):
        # channel_id → set of connected WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Total connection count for monitoring
        self._total_connected = 0

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept and register a WebSocket into a channel."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        self._total_connected += 1
        logger.info(f"[WS] Client connected to channel '{channel}' | Total: {self._total_connected}")

    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a WebSocket from its channel on disconnect."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        self._total_connected = max(0, self._total_connected - 1)
        logger.info(f"[WS] Client disconnected from channel '{channel}' | Total: {self._total_connected}")

    async def broadcast(self, channel: str, data: dict):
        """
        Push data to all WebSocket clients in a channel.
        This is the "push" in push-based architecture.
        Failed/dead connections are cleaned up automatically.
        """
        if channel not in self.active_connections:
            return

        failed = set()
        for ws in self.active_connections[channel].copy():
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning(f"[WS] Broadcast to {channel} failed for a connection: {e}")
                failed.add(ws)

        # Cleanup dead connections
        for ws in failed:
            self.active_connections[channel].discard(ws)

    async def send_initial_state(self, websocket: WebSocket, delivery_id: str):
        """
        When a new client connects, immediately send the last known location
        from cache — so the map loads instantly without waiting for next GPS ping.
        """
        cached = await location_cache.get_by_delivery(delivery_id)
        if cached:
            await websocket.send_json({
                "type": "initial_location",
                "delivery_id": delivery_id,
                "location": {
                    "latitude": cached["latitude"],
                    "longitude": cached["longitude"]
                },
                "status": cached.get("status", "in_transit"),
                "speed_kmh": cached.get("speed_kmh"),
                "heading": cached.get("heading"),
                "battery_level": cached.get("battery_level"),
                "timestamp": cached.get("timestamp"),
                "cache_age_seconds": cached.get("cache_age_seconds", 0)
            })
            logger.debug(f"[WS] Sent cached initial state for delivery {delivery_id}")

    def get_stats(self) -> dict:
        return {
            "total_connected": self._total_connected,
            "channels": {ch: len(ws_set) for ch, ws_set in self.active_connections.items()},
            "channel_count": len(self.active_connections)
        }


# SSE subscriber registry: delivery_id → list of asyncio.Queue
_sse_subscribers: Dict[str, list] = {}

manager = ConnectionManager()


# ─────────────────────────────────────────────────
#  Core Location Update Endpoint
#  Called by rider's app every few seconds via GPS
# ─────────────────────────────────────────────────

@router.post("/location")
async def update_location(
    update: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Rider GPS update endpoint.
    
    Called by the delivery partner's app every ~5-15 seconds.
    
    Pipeline:
    1. Validate rider identity
    2. Save to DB (for persistence/history)
    3. Update in-memory cache (O(1), for instant reads)
    4. Broadcast via WebSocket to per-order channel
    5. Broadcast to live_fleet (dispatchers)
    6. Push to SSE subscribers
    7. Check route deviation
    
    This endpoint is on the "hot path" — must stay fast.
    """
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

    # ① Persist to database (location history)
    try:
        db_service.save_location_update(location_data)
    except Exception as e:
        logger.error(f"DB write failed for location update: {e}")
        # Don't fail the endpoint — cache + broadcast can still work

    # ② Update H3 Geospatial Index
    try:
        geo_service.update_rider_location(
            rider_id=current_user.id,
            latitude=update.latitude,
            longitude=update.longitude
        )
    except Exception as e:
        logger.warning(f"Geo service update failed: {e}")

    # ③ Check route deviation (only if route_id provided)
    reoptimization_needed = False
    if update.route_id:
        try:
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
        except Exception as e:
            logger.warning(f"Route deviation check failed: {e}")

    # ④ Update in-memory cache (FAST — dictionary write)
    await location_cache.set_location(
        delivery_id=update.delivery_id,
        rider_id=current_user.id,
        latitude=update.latitude,
        longitude=update.longitude,
        status=update.status,
        speed_kmh=update.speed_kmh,
        heading=update.heading,
        battery_level=update.battery_level,
        reoptimization_needed=reoptimization_needed
    )

    # ⑤ Build broadcast payload
    broadcast_data = {
        "type": "location_update",
        "rider_id": current_user.id,
        "delivery_id": update.delivery_id,
        "location": {"latitude": update.latitude, "longitude": update.longitude},
        "status": update.status,
        "speed_kmh": update.speed_kmh,
        "heading": update.heading,
        "battery_level": update.battery_level,
        "timestamp": datetime.utcnow().isoformat(),
        "reoptimization_needed": reoptimization_needed
    }

    # ⑥ WebSocket broadcast: per-order channel (customer watching their order)
    await manager.broadcast(update.delivery_id, broadcast_data)

    # ⑦ WebSocket broadcast: global fleet channel (dispatchers/admins)
    await manager.broadcast("live_fleet", broadcast_data)

    # ⑧ SSE push: notify any SSE subscribers
    await _push_to_sse_subscribers(update.delivery_id, broadcast_data)

    # ⑨ System-wide notification broadcast
    await notification_manager.broadcast({
        "type": "rider_location_update",
        "data": broadcast_data
    })

    logger.debug(
        f"Location update: rider={current_user.id} "
        f"delivery={update.delivery_id} "
        f"lat={update.latitude:.4f} lng={update.longitude:.4f}"
    )

    return {
        "success": True,
        "reoptimization_needed": reoptimization_needed,
        "cached": True
    }


# ─────────────────────────────────────────────────
#  Cache-First Location Read
#  Instant response — no DB hit
# ─────────────────────────────────────────────────

@router.get("/current/{delivery_id}")
async def get_current_location(delivery_id: str):
    """
    Get the latest location for a delivery.
    
    Cache-first: reads from in-memory cache (O(1)), falls back to DB only if
    cache is cold (e.g., after server restart).
    
    This endpoint powers the "where is my rider?" query on the customer dashboard.
    """
    # ① Try cache first (zero DB queries)
    cached = await location_cache.get_by_delivery(delivery_id)
    if cached:
        return {
            "success": True,
            "source": "cache",
            "data": cached
        }

    # ② Cache miss → fall back to DB
    from database.database import SessionLocal
    db = SessionLocal()
    try:
        db_service = DatabaseService(db)
        tracking_data = db_service.get_delivery_tracking(delivery_id, limit=1)
        return {
            "success": True,
            "source": "database",
            "data": tracking_data
        }
    finally:
        db.close()


@router.get("/fleet")
async def get_fleet_locations():
    """
    Get all active rider locations for fleet monitoring.
    Returns cache snapshot — no DB needed.
    Used by dispatcher dashboard for real-time fleet overview.
    """
    fleet = await location_cache.get_all_fleet()
    return {
        "success": True,
        "source": "cache",
        "rider_count": len(fleet),
        "fleet": fleet
    }


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Cache performance metrics.
    Shows hit rate, active entries, etc.
    Useful for monitoring and interviews: 'how efficient is your cache?'
    """
    stats = location_cache.get_stats()
    ws_stats = manager.get_stats()
    return {
        "cache": stats,
        "websocket": ws_stats,
        "sse_channels": len(_sse_subscribers)
    }


# ─────────────────────────────────────────────────
#  WebSocket: Per-Order and Fleet Channels
# ─────────────────────────────────────────────────

@router.websocket("/live/{channel}")
async def websocket_tracking(websocket: WebSocket, channel: str):
    """
    WebSocket endpoint for live tracking.
    
    Channel can be:
    - delivery_id: customer watching a specific delivery
    - 'live_fleet': dispatcher watching all riders on map
    
    Push-based: server pushes updates to ALL connected clients
    in the channel when a rider GPS ping arrives.
    
    On connect: immediately sends latest cached location
    so the map shows something instantly.
    """
    await manager.connect(websocket, channel)

    # Send cached initial state immediately on connect
    if channel != "live_fleet":
        await manager.send_initial_state(websocket, channel)
    else:
        # For fleet view, send snapshot of all active riders
        fleet = await location_cache.get_all_fleet()
        if fleet:
            await websocket.send_json({
                "type": "fleet_snapshot",
                "riders": list(fleet.values()),
                "count": len(fleet),
                "timestamp": datetime.utcnow().isoformat()
            })

    try:
        while True:
            # Keep connection alive; handle ping/pong
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            except asyncio.TimeoutError:
                # Send keepalive ping every 30s
                try:
                    await websocket.send_json({"type": "keepalive", "timestamp": datetime.utcnow().isoformat()})
                except Exception:
                    break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning(f"[WS] Unexpected error in channel '{channel}': {e}")
    finally:
        manager.disconnect(websocket, channel)


# ─────────────────────────────────────────────────
#  SSE: Server-Sent Events (Browser-native fallback)
#  Works when WebSocket is blocked by proxies/firewalls
# ─────────────────────────────────────────────────

async def _push_to_sse_subscribers(delivery_id: str, data: Dict[str, Any]):
    """Push a location update to all SSE subscribers for this delivery."""
    if delivery_id not in _sse_subscribers:
        return

    dead_queues = []
    for queue in _sse_subscribers[delivery_id]:
        try:
            queue.put_nowait(data)
        except asyncio.QueueFull:
            dead_queues.append(queue)

    for q in dead_queues:
        _sse_subscribers[delivery_id].remove(q)


@router.get("/stream/{delivery_id}")
async def sse_location_stream(delivery_id: str, request: Request):
    """
    Server-Sent Events stream for live GPS tracking.
    
    SSE vs WebSocket:
    - SSE is one-way (server → client), simpler, works over HTTP/1.1
    - WebSocket is bidirectional
    - SSE reconnects automatically in browsers
    - Better for read-only consumers like customer tracking pages
    
    Browser usage:
        const es = new EventSource('/api/v1/tracking/stream/{delivery_id}');
        es.onmessage = (e) => updateMarker(JSON.parse(e.data));
    """
    queue: asyncio.Queue = asyncio.Queue(maxsize=50)

    if delivery_id not in _sse_subscribers:
        _sse_subscribers[delivery_id] = []
    _sse_subscribers[delivery_id].append(queue)

    logger.info(f"[SSE] Client connected to stream for delivery {delivery_id}")

    async def event_generator():
        # Send initial cached location immediately
        cached = await location_cache.get_by_delivery(delivery_id)
        if cached:
            yield f"event: initial_location\ndata: {json.dumps(cached)}\n\n"

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    # Wait for next location update
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"event: location_update\ndata: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive comment to prevent connection timeout
                    yield f": keepalive\n\n"

        except asyncio.CancelledError:
            pass
        finally:
            if delivery_id in _sse_subscribers:
                try:
                    _sse_subscribers[delivery_id].remove(queue)
                    if not _sse_subscribers[delivery_id]:
                        del _sse_subscribers[delivery_id]
                except ValueError:
                    pass
            logger.info(f"[SSE] Client disconnected from stream for delivery {delivery_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )


# ─────────────────────────────────────────────────
#  GPS Simulator (Development/Demo only)
#  Simulates a rider moving along a path
# ─────────────────────────────────────────────────

@router.post("/simulate/{delivery_id}")
async def simulate_gps_movement(
    delivery_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    GPS simulation for testing without a real device.
    Moves a simulated rider along a predefined path in Coimbatore.
    
    Used for demos and development. In production, real GPS comes
    from the rider's mobile app every 5-15 seconds.
    """
    # Coimbatore route: moves from one point to another across 10 steps
    path = [
        (11.0168, 76.9558),  # Start: RS Puram
        (11.0190, 76.9600),
        (11.0215, 76.9640),
        (11.0240, 76.9680),
        (11.0265, 76.9715),
        (11.0290, 76.9750),
        (11.0310, 76.9790),
        (11.0333, 76.9825),  # Mid: Gandhipuram
        (11.0355, 76.9860),
        (11.0375, 76.9895),
        (11.0400, 76.9930),  # End: Ukkadam
    ]

    import random

    # Run simulation in background — don't block the response
    async def run_simulation():
        for i, (lat, lng) in enumerate(path):
            # Add small random jitter to simulate real GPS
            lat += random.uniform(-0.0002, 0.0002)
            lng += random.uniform(-0.0002, 0.0002)
            speed = random.uniform(20, 45)
            heading = (i / len(path)) * 360

            await location_cache.set_location(
                delivery_id=delivery_id,
                rider_id=current_user.id,
                latitude=lat,
                longitude=lng,
                status="in_transit",
                speed_kmh=speed,
                heading=heading,
                battery_level=max(20, 100 - i * 5)
            )

            broadcast_data = {
                "type": "location_update",
                "rider_id": current_user.id,
                "delivery_id": delivery_id,
                "location": {"latitude": lat, "longitude": lng},
                "status": "in_transit",
                "speed_kmh": speed,
                "heading": heading,
                "battery_level": max(20, 100 - i * 5),
                "timestamp": datetime.utcnow().isoformat(),
                "reoptimization_needed": False,
                "is_simulated": True
            }

            await manager.broadcast(delivery_id, broadcast_data)
            await manager.broadcast("live_fleet", broadcast_data)
            await _push_to_sse_subscribers(delivery_id, broadcast_data)

            # Wait 3 seconds between GPS pings (simulating real device interval)
            await asyncio.sleep(3)

        # Mark delivery as completed
        final_data = {
            "type": "status_change",
            "delivery_id": delivery_id,
            "status": "delivered",
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast(delivery_id, final_data)
        await _push_to_sse_subscribers(delivery_id, final_data)
        logger.info(f"[SIM] GPS simulation completed for delivery {delivery_id}")

    # Start simulation as background task
    asyncio.create_task(run_simulation())

    return {
        "success": True,
        "message": f"GPS simulation started for delivery {delivery_id}",
        "waypoints": len(path),
        "interval_seconds": 3,
        "total_duration_seconds": len(path) * 3
    }


# ─────────────────────────────────────────────────
#  Cache Cleanup Background Task
# ─────────────────────────────────────────────────

async def periodic_cache_cleanup():
    """Cleanup expired cache entries every 60 seconds."""
    while True:
        await asyncio.sleep(60)
        cleaned = await location_cache.cleanup_expired()
        if cleaned > 0:
            logger.debug(f"Periodic cache cleanup: removed {cleaned} stale entries")
