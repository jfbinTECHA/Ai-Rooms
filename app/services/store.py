from __future__ import annotations

import asyncio
import uuid
from typing import Dict, List

from app.schemas import CreateNomi, CreateRoom, Message, Nomi, Room, RoomMessagesResponse


class InMemoryStore:
    """Thread-safe-ish in-memory data store for prototypes."""

    def __init__(self, history_limit: int = 50) -> None:
        self._nomis: Dict[str, Nomi] = {}
        self._rooms: Dict[str, Room] = {}
        self._messages: Dict[str, List[Message]] = {}
        self._history_limit = history_limit
        self._lock = asyncio.Lock()

    async def create_nomi(self, payload: CreateNomi) -> Nomi:
        nomi_id = str(uuid.uuid4())
        nomi = Nomi(id=nomi_id, name=payload.name, persona=payload.persona)
        async with self._lock:
            self._nomis[nomi_id] = nomi
        return nomi

    async def get_nomi(self, nomi_id: str) -> Optional[Nomi]:
        async with self._lock:
            return self._nomis.get(nomi_id)

    async def create_room(self, payload: CreateRoom) -> Room:
        room_id = str(uuid.uuid4())
        room = Room(id=room_id, name=payload.name)
        async with self._lock:
            self._rooms[room_id] = room
            self._messages.setdefault(room_id, [])
        return room

    async def room_exists(self, room_id: str) -> bool:
        async with self._lock:
            return room_id in self._rooms

    async def list_rooms(self) -> List[Room]:
        async with self._lock:
            return list(self._rooms.values())

    async def get_room_messages(self, room_id: str) -> RoomMessagesResponse:
        async with self._lock:
            messages = self._messages.get(room_id, [])
            # copy to avoid accidental external mutation
            return RoomMessagesResponse(messages=[msg.model_copy() for msg in messages])

    async def append_room_message(self, room_id: str, message: Message) -> None:
        async with self._lock:
            history = self._messages.setdefault(room_id, [])
            history.append(message)
            if len(history) > self._history_limit:
                del history[:-self._history_limit]
