from fastapi import WebSocket, WebSocketDisconnect
from typing import List


class EventManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.remove(websocket)

    async def broadcast_to_all(self, message: dict):
        """Send a message to all active connections"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                await self.disconnect(connection)


event_manager = EventManager()
