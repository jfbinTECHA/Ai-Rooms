from fastapi import FastAPI

from app.api.http import router as http_router
from app.api.ws import router as ws_router
from app.services.embeddings import EmbeddingsWorker
from app.services.rooms import RoomManager
from app.services.store import InMemoryStore


def create_app() -> FastAPI:
    app = FastAPI(title="AI Rooms – Minimal Stack", version="0.1.0")

    store = InMemoryStore()
    room_manager = RoomManager(store)
    embeddings_worker = EmbeddingsWorker()

    app.state.store = store
    app.state.room_manager = room_manager
    app.state.embeddings_worker = embeddings_worker

    app.include_router(http_router)
    app.include_router(ws_router)

    @app.on_event("startup")
    async def on_startup() -> None:  # pragma: no cover - Lifespan event
        await embeddings_worker.start()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:  # pragma: no cover - Lifespan event
        await embeddings_worker.shutdown()

    @app.get("/health", tags=["system"])
    async def health_check() -> dict:
        rooms = await store.list_rooms()
        return {
            "status": "healthy",
            "rooms": len(rooms),
        }

    return app


app = create_app()
