from fastapi import APIRouter, Depends

from backend.backend_service.dependencies import get_store
from backend.backend_service.schemas import UsageResponse
from backend.backend_service.services.security import get_current_user
from backend.backend_service.services.store import DatabaseStore

router = APIRouter(tags=["system"])


@router.get("/")
async def root() -> dict:
    return {"message": "Welcome to AI Rooms Backend API"}


@router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy"}


@router.get("/models")
async def get_models() -> dict:
    return {"models": ["gpt-3.5", "local-model"]}


@router.post("/chat")
async def chat(message: str) -> dict:
    return {"response": f"Echo: {message}"}


@router.get("/api/v1/usage", response_model=UsageResponse)
def get_usage(
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> UsageResponse:
    usage = store.get_usage(current_user.id)
    return UsageResponse(usage=usage)
