from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
from ..services.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, channel: Optional[str] = "all"):
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = eval(data) if data else {}
                if message.get("type") == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket, "alerts")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")


@router.websocket("/ws/health")
async def websocket_health(websocket: WebSocket):
    await manager.connect(websocket, "health")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "health")


@router.get("/api/ws/stats")
async def websocket_stats():
    return {
        "total_connections": manager.get_connection_count("all"),
        "alert_connections": manager.get_connection_count("alerts"),
        "health_connections": manager.get_connection_count("health"),
        "prediction_connections": manager.get_connection_count("predictions")
    }