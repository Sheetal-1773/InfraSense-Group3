import asyncio
import json
from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "alerts": set(),
            "health": set(),
            "predictions": set(),
            "all": set()
        }
    
    async def connect(self, websocket: WebSocket, channel: str = "all"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        logger.info(f"WebSocket disconnected from channel: {channel}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: dict, channel: str = "all"):
        disconnected = []
        
        for websocket in self.active_connections.get(channel, set()):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to websocket: {e}")
                disconnected.append(websocket)
        
        for ws in disconnected:
            self.disconnect(ws, channel)
    
    async def broadcast_alert(self, alert: dict):
        message = {
            "type": "alert",
            "data": alert,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message, "alerts")
        await self.broadcast(message, "all")
    
    async def broadcast_health_update(self, component_id: str, health_score: int, status: str):
        message = {
            "type": "health_update",
            "data": {
                "component_id": component_id,
                "health_score": health_score,
                "status": status
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message, "health")
        await self.broadcast(message, "all")
    
    async def broadcast_prediction(self, prediction: dict):
        message = {
            "type": "prediction",
            "data": prediction,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message, "predictions")
        await self.broadcast(message, "all")
    
    def get_connection_count(self, channel: str = "all") -> int:
        return len(self.active_connections.get(channel, set()))


manager = ConnectionManager()


async def notify_new_alert(alert_data: dict):
    await manager.broadcast_alert(alert_data)


async def notify_health_update(component_id: str, health_score: int, status: str):
    await manager.broadcast_health_update(component_id, health_score, status)


async def notify_prediction(prediction_data: dict):
    await manager.broadcast_prediction(prediction_data)