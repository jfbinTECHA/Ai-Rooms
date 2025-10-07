from fastapi import APIRouter, Depends

from backend.backend_service.dependencies import get_store
from backend.backend_service.schemas import EmbeddingRequest, EmbeddingResponse, SearchResult
from backend.backend_service.services.embeddings import deterministic_embedding
from backend.backend_service.services.security import get_current_user
from backend.backend_service.services.store import DatabaseStore

router = APIRouter(prefix="/api/v1", tags=["embeddings"])


@router.post("/embeddings", response_model=EmbeddingResponse, status_code=201)
def create_embedding(
    payload: EmbeddingRequest,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> EmbeddingResponse:
    vector = deterministic_embedding(payload.text)
    record = store.create_embedding(payload.text, vector, payload.metadata or {})
    store.increment_usage(current_user.id)
    return EmbeddingResponse(id=record.id)


@router.get("/search", response_model=list[SearchResult])
def search_embeddings(
    query: str,
    k: int = 8,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> list[SearchResult]:
    store.increment_usage(current_user.id)
    return store.search_embeddings(query, k)
