# app/core/websocket_manager.py
from typing import Dict, List
from fastapi import WebSocket
import json
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # Store active connections: {user_id: [websockets]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user's WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a user's WebSocket"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Remove user if no connections left
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        print(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user across all their connections"""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Error sending to user {user_id}: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.disconnect(ws, user_id)
    
    async def send_notification(self, notification: dict, user_id: int):
        """Send a notification to a user"""
        notification_message = {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(notification_message, user_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)
    
    def is_user_online(self, user_id: int) -> bool:
        """Check if a user is online"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_online_user_count(self) -> int:
        """Get total number of online users"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()