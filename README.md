# AI Rooms Monorepo

This repository houses a set of lightweight services that demonstrate the AI Rooms platform. Each service is self-contained, but they can be run together via Docker for a full-stack prototype.

## Services
- **app/** – Minimal FastAPI application that exposes room chat REST/WebSocket endpoints and a deterministic embedding worker for experimentation.
- **backend/** – Authenticated FastAPI backend featuring user/nomi/room management, embeddings CRUD, and integration-style tests backed by a SQLAlchemy store (SQLite by default).
- **websocket/** – Standalone WebSocket broadcaster used for early room-event prototyping.
- **model_workers/**, **embeddings_worker/** – Worker stubs that can be swapped for real inference or vector generation backends.
- **infra/** – Shared configuration (Redis, Postgres init scripts, nginx, Kubernetes manifests).
- **monitoring/** – Prometheus, Grafana, Jaeger, and Loki configuration for observability experiments.

## Local Development

```bash
make venv           # create a repo-wide virtualenv (./.venv)
make install-app    # install app service dependencies
make install-backend
make run-app        # run the sandbox FastAPI app at :8004
make run-backend    # run the authenticated backend at :8000
```

You can always activate the environment manually via `source .venv/bin/activate` and run the `uvicorn` commands printed by the Makefile.

## Testing

```bash
make test-app
make test-backend
```

The app tests exercise REST flows for rooms and embeddings; the backend tests walk through a signup-to-search lifecycle.

## Docker & Compose

```bash
docker compose up --build
```

The compose file launches nginx, Postgres, Redis, MinIO, monitoring services, and the application containers. For local iteration you typically run the FastAPI apps directly and rely on Docker only when validating integration.

## Contributing

1. Run the relevant `make install-*` target.
2. Implement your changes.
3. Execute `make test-app` / `make test-backend`.
4. Follow up with docker-compose testing if your changes affect container builds.

Feel free to expand the Makefile targets as the stack grows (linting, formatting, migrations, etc.).
