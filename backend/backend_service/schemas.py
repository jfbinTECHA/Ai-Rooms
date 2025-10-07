from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenResponse(Token):
    pass


class NomiCreate(BaseModel):
    name: str
    persona: Dict[str, str] = Field(default_factory=dict)
    default_model: str = "gpt-3.5-turbo"
    avatar_url: Optional[str] = None
    visibility: str = "private"


class NomiUpdate(BaseModel):
    name: Optional[str] = None
    persona: Optional[Dict[str, str]] = None
    default_model: Optional[str] = None
    avatar_url: Optional[str] = None
    visibility: Optional[str] = None


class Nomi(BaseModel):
    id: str
    owner_id: str
    name: str
    persona: Dict[str, str] = Field(default_factory=dict)
    default_model: str
    avatar_url: Optional[str] = None
    visibility: str = "private"
    created_at: datetime
    updated_at: datetime


class RoomCreate(BaseModel):
    name: str
    is_group: bool = False


class Room(BaseModel):
    id: str
    owner_id: str
    name: str
    is_group: bool = False
    members: List[str] = Field(default_factory=list)
    created_at: datetime


class MessageCreate(BaseModel):
    text: str
    content: Optional[Dict[str, str]] = None


class Message(BaseModel):
    id: str
    room_id: str
    sender_id: str
    text: str
    content: Optional[Dict[str, str]] = None
    created_at: datetime


class ChatRequest(BaseModel):
    message: str
    async_mode: bool = False


class ChatResponse(BaseModel):
    message_id: str
    reply: str


class EmbeddingRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, str]] = None


class EmbeddingRecord(BaseModel):
    id: str
    text: str
    vector: List[float]
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime


class EmbeddingResponse(BaseModel):
    id: str
    status: str = "created"


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: Dict[str, str] = Field(default_factory=dict)


class ModelOverride(BaseModel):
    model: str
    config: Optional[Dict[str, str]] = None


class UsageResponse(BaseModel):
    usage: Dict[str, int] = Field(default_factory=dict)
