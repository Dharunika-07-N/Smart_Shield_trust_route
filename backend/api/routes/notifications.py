from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
from loguru import logger
import json

router = APIRouter()

class NotificationManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected to notifications. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected from notifications. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
            
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting notification: {e}")
                disconnected.add(connection)
        
        for connection in disconnected:
            self.active_connections.remove(connection)

    def broadcast_sync(self, message: dict):
        """Thread-safe and sync-safe broadcast."""
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    loop.create_task(self.broadcast(message))
                    return
            except RuntimeError:
                pass
            
            # Fallback for sync contexts
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(self.broadcast(message))
            new_loop.close()
        except Exception as e:
            logger.error(f"Error in sync broadcast: {e}")

manager = NotificationManager()

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, wait for client messages if any
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket notification error: {e}")
        manager.disconnect(websocket)
