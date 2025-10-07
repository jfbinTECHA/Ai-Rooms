import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.dependencies import get_room_manager_ws, get_store_ws
from app.schemas import Message
from app.services.rooms import RoomManager
from app.services.store import InMemoryStore

router = APIRouter()


@router.websocket("/ws/rooms/{room_id}")
async def room_websocket(
    websocket: WebSocket,
    room_id: str,
    store: InMemoryStore = Depends(get_store_ws),
    room_manager: RoomManager = Depends(get_room_manager_ws),
) -> None:
    if not await store.room_exists(room_id):
        await websocket.close(code=4000)
        return

    await room_manager.connect(room_id, websocket)
    try:
        while True:
            text = await websocket.receive_text()
            message = Message(
                id=str(uuid.uuid4()),
                roomId=room_id,
                sender="client",
                text=text,
            )
            await store.append_room_message(room_id, message)
            await room_manager.broadcast(room_id, message)
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, websocket)
    except Exception:
        await room_manager.disconnect(room_id, websocket)
        await websocket.close(code=1011)
