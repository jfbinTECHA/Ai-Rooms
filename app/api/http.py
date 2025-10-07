import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_embeddings_worker, get_room_manager, get_store
from app.schemas import (
    BroadcastMessage,
    BroadcastResponse,
    ChatBody,
    ChatResponse,
    CreateNomi,
    CreateRoom,
    EmbeddingRequest,
    EmbeddingResponse,
    Message,
    Nomi,
    Room,
    RoomMessagesResponse,
)
from app.services.embeddings import EmbeddingsWorker
from app.services.rooms import RoomManager
from app.services.store import InMemoryStore

router = APIRouter(prefix="/api/v1")


@router.post("/nomis", response_model=Nomi, status_code=status.HTTP_201_CREATED)
async def create_nomi(
    payload: CreateNomi, store: InMemoryStore = Depends(get_store)
) -> Nomi:
    return await store.create_nomi(payload)


@router.post("/rooms", response_model=Room, status_code=status.HTTP_201_CREATED)
async def create_room(
    payload: CreateRoom, store: InMemoryStore = Depends(get_store)
) -> Room:
    return await store.create_room(payload)


@router.get(
    "/rooms/{room_id}/messages",
    response_model=RoomMessagesResponse,
    responses={404: {"description": "Room not found"}},
)
async def get_room_messages(
    room_id: str, store: InMemoryStore = Depends(get_store)
) -> RoomMessagesResponse:
    if not await store.room_exists(room_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="room not found")
    return await store.get_room_messages(room_id)


@router.post(
    "/rooms/{room_id}/broadcast",
    response_model=BroadcastResponse,
    responses={404: {"description": "Room not found"}},
)
async def broadcast_to_room(
    room_id: str,
    payload: BroadcastMessage,
    store: InMemoryStore = Depends(get_store),
    room_manager: RoomManager = Depends(get_room_manager),
) -> BroadcastResponse:
    if not await store.room_exists(room_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="room not found")

    message = Message(
        id=str(uuid.uuid4()),
        roomId=room_id,
        sender=payload.sender or "system",
        text=payload.messageText,
    )
    await store.append_room_message(room_id, message)
    delivered = await room_manager.broadcast(room_id, message)
    return BroadcastResponse(delivered=delivered, message=message)


@router.post(
    "/nomis/{nomi_id}/chat",
    response_model=ChatResponse,
    responses={
        404: {"description": "Nomi or room not found"},
    },
)
async def chat_nomi(
    nomi_id: str,
    payload: ChatBody,
    store: InMemoryStore = Depends(get_store),
    embeddings: EmbeddingsWorker = Depends(get_embeddings_worker),
    room_manager: RoomManager = Depends(get_room_manager),
) -> ChatResponse:
    nomi = await store.get_nomi(nomi_id)
    if not nomi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="nomi not found")

    if payload.roomId and not await store.room_exists(payload.roomId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="room not found")

    embedding = await embeddings.embed(payload.messageText)
    message = Message(
        id=str(uuid.uuid4()),
        roomId=payload.roomId,
        sender=f"nomi:{nomi.name}",
        text=f"{nomi.name} echoes: {payload.messageText}",
        embedding=embedding,
        nomiId=nomi.id,
    )

    if payload.roomId:
        await store.append_room_message(payload.roomId, message)
        await room_manager.broadcast(payload.roomId, message)

    return ChatResponse(message=message)


@router.post(
    "/embeddings",
    response_model=EmbeddingResponse,
)
async def generate_embedding(
    payload: EmbeddingRequest,
    embeddings: EmbeddingsWorker = Depends(get_embeddings_worker),
) -> EmbeddingResponse:
    vector = await embeddings.embed(payload.text)
    return EmbeddingResponse(embedding=vector)
