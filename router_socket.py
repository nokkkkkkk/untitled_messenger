from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket

    def disconnect(self, room_id: int, user_id: int):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: int, sender_id: int):
        if room_id in self.active_connections:
            for uid, conn in self.active_connections[room_id].items():
                await conn.send_json({
                    'text': message,
                    'is_self': uid == sender_id
                })

manager = ConnectionManager()
router = APIRouter(prefix="/ws/chat")

@router.websocket("/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: int, 
    user_id: int, 
    username: str = Query(...)
):
    await manager.connect(websocket, room_id, user_id)
    await manager.broadcast(f"{username} (ID: {user_id}) присоединился к чату.", room_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{username} (ID: {user_id}): {data}", room_id, user_id)
    except WebSocketDisconnect:
        manager.disconnect(room_id, user_id)
        await manager.broadcast(f"{username} (ID: {user_id}) покинул чат.", room_id, user_id)
