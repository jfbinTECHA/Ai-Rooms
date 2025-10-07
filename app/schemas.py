from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CreateNomi(BaseModel):
    name: str
    persona: Dict[str, str] = Field(default_factory=dict)


class Nomi(BaseModel):
    id: str
    name: str
    persona: Dict[str, str] = Field(default_factory=dict)


class ChatBody(BaseModel):
    messageText: str
    roomId: Optional[str] = None


class CreateRoom(BaseModel):
    name: str


class Room(BaseModel):
    id: str
    name: str


class BroadcastMessage(BaseModel):
    messageText: str
    sender: Optional[str] = None


class EmbeddingRequest(BaseModel):
    text: str


class EmbeddingResponse(BaseModel):
    embedding: List[float]


class Message(BaseModel):
    id: str
    roomId: Optional[str] = None
    sender: str
    text: str
    embedding: Optional[List[float]] = None
    nomiId: Optional[str] = None


class BroadcastResponse(BaseModel):
    delivered: int
    message: Message


class RoomMessagesResponse(BaseModel):
    messages: List[Message]


class ChatResponse(BaseModel):
    message: Message
