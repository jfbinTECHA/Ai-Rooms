# AI Rooms Backend Service

The backend service provides authenticated REST APIs for managing nomis, rooms, embeddings, and model overrides. Data is persisted with SQLAlchemy against SQLite by default, and the store can be pointed at Postgres (or another SQL backend) via `AI_ROOMS_DATABASE_URL`.

## Getting Started

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn backend.main:app --reload
```

The OpenAPI docs are available at `http://localhost:8000/docs` once the server is running.

## Testing

```bash
pytest
```

The suite performs an end-to-end flow covering sign-up, nomi creation, room messaging, embeddings, search, and usage tracking.

## Docker

```bash
docker build -t ai-rooms-backend .
docker run -p 8000:8000 ai-rooms-backend
```

## Next Steps

- Swap the default SQLite database for Postgres/Redis in production environments.
- Forward chat and embedding requests to the model and embeddings workers.
- Expand the test suite with async WebSocket coverage and error-path assertions.
