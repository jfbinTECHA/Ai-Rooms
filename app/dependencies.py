from fastapi import Request, WebSocket

from app.services.embeddings import EmbeddingsWorker
from app.services.rooms import RoomManager
from app.services.store import InMemoryStore


def get_store(request: Request) -> InMemoryStore:
    return request.app.state.store


def get_room_manager(request: Request) -> RoomManager:
    return request.app.state.room_manager


def get_embeddings_worker(request: Request) -> EmbeddingsWorker:
    return request.app.state.embeddings_worker


def get_store_ws(websocket: WebSocket) -> InMemoryStore:
    return websocket.app.state.store


def get_room_manager_ws(websocket: WebSocket) -> RoomManager:
    return websocket.app.state.room_manager
