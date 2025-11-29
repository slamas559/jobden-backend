# app/api/api_v1/endpoints/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.websocket_manager import manager
from app.core.security import decode_access_token
from app.db.database import get_db
from app.services.notification_service import get_user_notifications

router = APIRouter()


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications
    
    Connect with: ws://localhost:8000/api/v1/ws/notifications?token=<your_access_token>
    """
    
    # Authenticate user from token
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Connect user
    await manager.connect(websocket, user_id)
    
    try:
        # Send connection success message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Successfully connected to notification stream",
            "user_id": user_id
        })
        
        # Send count of unread notifications on connection
        from app.services.notification_service import get_unread_count
        unread_count = await get_unread_count(db, user_id)
        await websocket.send_json({
            "type": "unread_count",
            "count": unread_count
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            # Receive messages from client (like "ping" for keep-alive)
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                })
            
            elif data.get("type") == "mark_read":
                # Client can request to mark notification as read
                notification_id = data.get("notification_id")
                if notification_id:
                    from app.services.notification_service import get_notification_by_id, mark_notification_as_read
                    notification = await get_notification_by_id(db, notification_id)
                    if notification and notification.user_id == user_id:
                        await mark_notification_as_read(db, notification)
                        await websocket.send_json({
                            "type": "notification_read",
                            "notification_id": notification_id
                        })
            
            elif data.get("type") == "get_unread_count":
                # Send current unread count
                from app.services.notification_service import get_unread_count
                unread_count = await get_unread_count(db, user_id)
                await websocket.send_json({
                    "type": "unread_count",
                    "count": unread_count
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        print(f"User {user_id} disconnected from notifications")
    
    except Exception as e:
        print(f"Error in WebSocket for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


@router.get("/online-status")
async def get_online_status():
    """Get current WebSocket connection statistics"""
    return {
        "online_users": manager.get_online_user_count(),
        "total_connections": sum(len(conns) for conns in manager.active_connections.values())
    }