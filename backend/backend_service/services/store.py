from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from backend.backend_service import models
from backend.backend_service.schemas import (
    EmbeddingRecord,
    Message,
    MessageCreate,
    ModelOverride,
    Nomi,
    NomiCreate,
    NomiUpdate,
    Room,
    RoomCreate,
    SearchResult,
    UserCreate,
)


class DatabaseStore:
    """Persistence layer backed by SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # Users -----------------------------------------------------------------
    def create_user(self, payload: UserCreate, hashed_password: str) -> models.User:
        existing = self.session.execute(
            select(models.User).where(models.User.email == payload.email)
        ).scalar_one_or_none()
        if existing:
            raise ValueError("user already exists")
        user = models.User(
            id=str(uuid.uuid4()),
            email=payload.email,
            display_name=payload.display_name,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        return self.session.execute(
            select(models.User).where(models.User.email == email)
        ).scalar_one_or_none()

    def get_user(self, user_id: str) -> Optional[models.User]:
        return self.session.get(models.User, user_id)

    # Nomis -----------------------------------------------------------------
    def create_nomi(self, owner_id: str, payload: NomiCreate) -> Nomi:
        nomi = models.Nomi(
            id=str(uuid.uuid4()),
            owner_id=owner_id,
            name=payload.name,
            persona=payload.persona or {},
            default_model=payload.default_model,
            avatar_url=payload.avatar_url,
            visibility=payload.visibility,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(nomi)
        self.session.commit()
        self.session.refresh(nomi)
        return _to_schema_nomi(nomi)

    def list_nomis(self, owner_id: str) -> List[Nomi]:
        nomis = self.session.execute(
            select(models.Nomi).where(models.Nomi.owner_id == owner_id)
        ).scalars()
        return [_to_schema_nomi(nomi) for nomi in nomis]

    def get_nomi(self, nomi_id: str, owner_id: Optional[str] = None) -> Optional[Nomi]:
        nomi = self.session.get(models.Nomi, nomi_id)
        if not nomi:
            return None
        if owner_id and nomi.owner_id != owner_id:
            return None
        return _to_schema_nomi(nomi)

    def update_nomi(self, nomi_id: str, payload: NomiUpdate) -> Optional[Nomi]:
        nomi = self.session.get(models.Nomi, nomi_id)
        if not nomi:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(nomi, field, value)
        nomi.updated_at = datetime.utcnow()
        self.session.add(nomi)
        self.session.commit()
        self.session.refresh(nomi)
        return _to_schema_nomi(nomi)

    def delete_nomi(self, nomi_id: str) -> bool:
        result = self.session.execute(
            delete(models.Nomi).where(models.Nomi.id == nomi_id)
        )
        self.session.commit()
        return result.rowcount > 0

    # Rooms -----------------------------------------------------------------
    def create_room(self, owner_id: str, payload: RoomCreate) -> Room:
        room = models.Room(
            id=str(uuid.uuid4()),
            owner_id=owner_id,
            name=payload.name,
            is_group=payload.is_group,
            created_at=datetime.utcnow(),
        )
        self.session.add(room)
        self.session.flush()
        membership = models.RoomMember(room_id=room.id, user_id=owner_id)
        self.session.add(membership)
        self.session.commit()
        self.session.refresh(room)
        return _to_schema_room(room, members=[owner_id])

    def list_rooms(self, user_id: str) -> List[Room]:
        rooms = (
            self.session.execute(
                select(models.Room)
                .join(models.RoomMember, models.RoomMember.room_id == models.Room.id)
                .where(models.RoomMember.user_id == user_id)
                .options(selectinload(models.Room.members))
                .distinct()
            )
            .scalars()
            .all()
        )
        return [_to_schema_room(room) for room in rooms]

    def get_room(self, room_id: str) -> Optional[Room]:
        room = (
            self.session.execute(
                select(models.Room)
                .where(models.Room.id == room_id)
                .options(selectinload(models.Room.members))
            )
            .scalars()
            .first()
        )
        if not room:
            return None
        return _to_schema_room(room)

    def join_room(self, room_id: str, user_id: str) -> Optional[Room]:
        room = self.session.get(models.Room, room_id)
        if not room:
            return None
        existing = self.session.execute(
            select(models.RoomMember).where(
                models.RoomMember.room_id == room_id,
                models.RoomMember.user_id == user_id,
            )
        ).scalar_one_or_none()
        if not existing:
            self.session.add(models.RoomMember(room_id=room_id, user_id=user_id))
            self.session.commit()
        room = (
            self.session.execute(
                select(models.Room)
                .where(models.Room.id == room_id)
                .options(selectinload(models.Room.members))
            )
            .scalars()
            .first()
        )
        return _to_schema_room(room) if room else None

    def add_message(self, room_id: str, user_id: str, payload: MessageCreate) -> Optional[Message]:
        if not self.session.get(models.Room, room_id):
            return None
        message = models.Message(
            id=str(uuid.uuid4()),
            room_id=room_id,
            sender_id=user_id,
            text=payload.text,
            content=payload.content,
            created_at=datetime.utcnow(),
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return _to_schema_message(message)

    def list_messages(self, room_id: str, limit: int = 50) -> List[Message]:
        messages = (
            self.session.execute(
                select(models.Message)
                .where(models.Message.room_id == room_id)
                .order_by(models.Message.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
        messages.reverse()
        return [_to_schema_message(message) for message in messages]

    # Embeddings ------------------------------------------------------------
    def create_embedding(self, text: str, vector: List[float], metadata: Dict[str, str]) -> EmbeddingRecord:
        record = models.Embedding(
            id=str(uuid.uuid4()),
            text=text,
            vector=vector,
            metadata=metadata,
            created_at=datetime.utcnow(),
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return _to_schema_embedding(record)

    def search_embeddings(self, query: str, k: int = 8) -> List[SearchResult]:
        query_lower = query.lower()
        embeddings = (
            self.session.execute(
                select(models.Embedding).where(
                    func.lower(models.Embedding.text).contains(query_lower)
                )
            )
            .scalars()
            .all()
        )
        results: List[SearchResult] = []
        for record in embeddings:
            if len(record.text) == 0:
                continue
            score = len(query_lower) / len(record.text)
            results.append(
                SearchResult(
                    id=record.id,
                    text=record.text,
                    score=round(score, 4),
                    metadata=record.metadata or {},
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:k]

    # Models ----------------------------------------------------------------
    def override_model(self, model_id: str, override: ModelOverride) -> None:
        existing = self.session.get(models.ModelOverride, model_id)
        if existing:
            existing.config = override.config or {}
            existing.updated_at = datetime.utcnow()
        else:
            existing = models.ModelOverride(
                model_id=model_id,
                config=override.config or {},
                updated_at=datetime.utcnow(),
            )
            self.session.add(existing)
        self.session.commit()

    # Usage -----------------------------------------------------------------
    def get_usage(self, user_id: str) -> Dict[str, int]:
        usage = self.session.get(models.Usage, user_id)
        return {user_id: usage.count if usage else 0}

    def increment_usage(self, user_id: str, amount: int = 1) -> None:
        usage = self.session.get(models.Usage, user_id)
        if usage:
            usage.count += amount
        else:
            usage = models.Usage(user_id=user_id, count=amount)
            self.session.add(usage)
        self.session.commit()


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #


def _to_schema_nomi(record: models.Nomi) -> Nomi:
    return Nomi(
        id=record.id,
        owner_id=record.owner_id,
        name=record.name,
        persona=record.persona or {},
        default_model=record.default_model,
        avatar_url=record.avatar_url,
        visibility=record.visibility,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _to_schema_room(record: models.Room, members: Optional[List[str]] = None) -> Room:
    member_ids = members if members is not None else [member.user_id for member in record.members]
    return Room(
        id=record.id,
        owner_id=record.owner_id,
        name=record.name,
        is_group=record.is_group,
        members=member_ids,
        created_at=record.created_at,
    )


def _to_schema_message(record: models.Message) -> Message:
    return Message(
        id=record.id,
        room_id=record.room_id,
        sender_id=record.sender_id,
        text=record.text,
        content=record.content,
        created_at=record.created_at,
    )


def _to_schema_embedding(record: models.Embedding) -> EmbeddingRecord:
    return EmbeddingRecord(
        id=record.id,
        text=record.text,
        vector=record.vector,
        metadata=record.metadata or {},
        created_at=record.created_at,
    )
