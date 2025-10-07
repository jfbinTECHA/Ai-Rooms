from fastapi import APIRouter, Depends

from backend.backend_service.dependencies import get_store
from backend.backend_service.schemas import ModelOverride
from backend.backend_service.services.security import get_current_user
from backend.backend_service.services.store import DatabaseStore

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.post("/{model_id}/override")
def override_model(
    model_id: str,
    payload: ModelOverride,
    store: DatabaseStore = Depends(get_store),
    current_user=Depends(get_current_user),
) -> dict:
    store.override_model(model_id, payload)
    store.increment_usage(current_user.id)
    return {"model_id": model_id, "overridden": True}
