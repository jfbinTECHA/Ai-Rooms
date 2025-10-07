# AI Rooms Minimal Service

This FastAPI service combines HTTP endpoints and a room-oriented WebSocket gateway so the rest of the stack can experiment with nomi chat flows without standing up the full microservice set.

## Features
- Create nomis and rooms via `/api/v1/nomis` and `/api/v1/rooms`.
- Chat with a nomi and optionally broadcast into a room, generating a deterministic hash-based “embedding” for quick experimentation.
- Broadcast arbitrary messages into a room and pull the last 50 messages from `/api/v1/rooms/{room_id}/messages`.
- Join room WebSockets at `/ws/rooms/{room_id}` to receive history replay plus live fan-out.

## Local Development
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Testing
```bash
pytest
```

The unit tests exercise the main REST endpoints and the embedding generator. WebSocket coverage can be added using `asyncio` clients once the stack evolves.
