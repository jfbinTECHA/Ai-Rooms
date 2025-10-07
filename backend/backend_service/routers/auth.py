from fastapi import APIRouter, Depends, HTTPException, status

from backend.backend_service.config import Settings
from backend.backend_service.dependencies import get_settings_dep, get_store
from backend.backend_service.schemas import TokenResponse, UserCreate, UserLogin
from backend.backend_service.services.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from backend.backend_service.services.store import DatabaseStore

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    payload: UserCreate,
    store: DatabaseStore = Depends(get_store),
    settings: Settings = Depends(get_settings_dep),
) -> TokenResponse:
    hashed_password = get_password_hash(payload.password)
    try:
        user = store.create_user(payload, hashed_password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    token = create_access_token(user.email, settings)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    store: DatabaseStore = Depends(get_store),
    settings: Settings = Depends(get_settings_dep),
) -> TokenResponse:
    user = store.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email, settings)
    return TokenResponse(access_token=token)


@router.post("/keys")
def create_api_key(
    current_user=Depends(get_current_user),
) -> dict:
    # Placeholder for API key generation. Use user ID to produce deterministic stub.
    api_key = f"key_{current_user.id[:8]}"
    return {"api_key": api_key}
