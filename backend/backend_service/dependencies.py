from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.backend_service.config import Settings
from backend.backend_service.services.store import DatabaseStore


def get_session(request: Request):
    session_factory = request.app.state.session_factory
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.close()


def get_store(session: Session = Depends(get_session)) -> DatabaseStore:
    return DatabaseStore(session)


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings
