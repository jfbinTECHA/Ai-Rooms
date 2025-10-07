from fastapi import APIRouter, Depends, HTTPException, status

from backend.backend_service.dependencies import get_store
from backend.backend_service.schemas import Message, MessageCreate, Room, RoomCreate
from backend.backend_service.services.security import get_current_user
from backend.backend_service.services.store import DatabaseStore

router = APIRouter(prefix="/api/v1/rooms", tags=["rooms"])


@router.get("/", response_model=list[Room])
def list_rooms(
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> list[Room]:
    return store.list_rooms(current_user.id)


@router.post("/", response_model=Room, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> Room:
    return store.create_room(current_user.id, payload)


@router.post("/{room_id}/join", response_model=Room)
def join_room(
    room_id: str,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> Room:
    room = store.join_room(room_id, current_user.id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.get("/{room_id}/messages", response_model=list[Message])
def get_room_messages(
    room_id: str,
    limit: int = 50,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> list[Message]:
    room = store.get_room(room_id)
    if not room or current_user.id not in room.members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return store.list_messages(room_id, limit)


@router.post("/{room_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
def send_message(
    room_id: str,
    payload: MessageCreate,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> Message:
    room = store.get_room(room_id)
    if not room or current_user.id not in room.members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    message = store.add_message(room_id, current_user.id, payload)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    store.increment_usage(current_user.id)
    return message
