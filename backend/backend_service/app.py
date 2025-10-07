from fastapi import FastAPI

from backend.backend_service import models
from backend.backend_service.config import get_settings
from backend.backend_service.database import create_session_factory
from backend.backend_service.routers import auth, embeddings, models as models_router, nomis, rooms, system


def create_app(database_url: str | None = None) -> FastAPI:
    base_settings = get_settings()
    settings = (
        base_settings.model_copy(update={"database_url": database_url})
        if database_url
        else base_settings
    )
    app = FastAPI(title="AI Rooms Backend API", version="1.0.0")

    engine, session_factory = create_session_factory(settings.database_url)
    models.Base.metadata.create_all(bind=engine)

    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.settings = settings

    # Include routers
    app.include_router(system.router)
    app.include_router(auth.router)
    app.include_router(nomis.router)
    app.include_router(rooms.router)
    app.include_router(embeddings.router)
    app.include_router(models_router.router)

    return app
