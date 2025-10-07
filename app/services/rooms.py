from __future__ import annotations

import asyncio
import json
from typing import Dict, List, Set

from fastapi import WebSocket

from app.schemas import Message, RoomMessagesResponse
from app.services.store import InMemoryStore


class RoomManager:
    """Maintains WebSocket connections per room and handles fan-out."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._rooms: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            connections = self._rooms.setdefault(room_id, set())
            connections.add(websocket)
        await self._send_history(room_id, websocket)

    async def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._rooms.get(room_id)
            if not connections:
                return
            connections.discard(websocket)
            if not connections:
                self._rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, message: Message) -> int:
        async with self._lock:
            connections: List[WebSocket] = list(self._rooms.get(room_id, set()))
        if not connections:
            return 0

        payload = json.dumps({"type": "message", "payload": message.model_dump()})
        delivered = 0
        for websocket in connections:
            try:
                await websocket.send_text(payload)
                delivered += 1
            except RuntimeError:
                # the connection is dead; it will be cleaned up at the next event
                continue
        return delivered

    async def _send_history(self, room_id: str, websocket: WebSocket) -> None:
        history: RoomMessagesResponse = await self._store.get_room_messages(room_id)
        for message in history.messages:
            payload = json.dumps({"type": "history", "payload": message.model_dump()})
            await websocket.send_text(payload)
