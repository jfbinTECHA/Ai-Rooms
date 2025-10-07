import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from backend.backend_service.dependencies import get_store
from backend.backend_service.schemas import ChatRequest, ChatResponse, Nomi, NomiCreate, NomiUpdate
from backend.backend_service.services.security import get_current_user
from backend.backend_service.services.store import DatabaseStore

router = APIRouter(prefix="/api/v1/nomis", tags=["nomis"])


@router.get("/", response_model=list[Nomi])
def list_nomis(
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> list[Nomi]:
    return store.list_nomis(current_user.id)


@router.post("/", response_model=Nomi, status_code=status.HTTP_201_CREATED)
def create_nomi(
    payload: NomiCreate,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> Nomi:
    return store.create_nomi(current_user.id, payload)


@router.get("/{nomi_id}", response_model=Nomi)
def get_nomi(
    nomi_id: str,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> Nomi:
    nomi = store.get_nomi(nomi_id, owner_id=current_user.id)
    if not nomi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nomi not found")
    return nomi


@router.patch("/{nomi_id}", response_model=Nomi)
def update_nomi(
    nomi_id: str,
    payload: NomiUpdate,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> Nomi:
    nomi = store.get_nomi(nomi_id, owner_id=current_user.id)
    if not nomi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nomi not found")
    updated = store.update_nomi(nomi_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nomi not found")
    return updated


@router.delete("/{nomi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nomi(
    nomi_id: str,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> None:
    nomi = store.get_nomi(nomi_id, owner_id=current_user.id)
    if not nomi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nomi not found")
    store.delete_nomi(nomi_id)


@router.post("/{nomi_id}/chat", response_model=ChatResponse)
def chat_with_nomi(
    nomi_id: str,
    payload: ChatRequest,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> ChatResponse:
    nomi = store.get_nomi(nomi_id, owner_id=current_user.id)
    if not nomi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nomi not found")
    fake_reply = f"{nomi.name} says: {payload.message}"
    reply_id = str(uuid.uuid4())
    store.increment_usage(current_user.id)
    return ChatResponse(message_id=reply_id, reply=fake_reply)
