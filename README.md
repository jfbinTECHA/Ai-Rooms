# AI Rooms Monorepo

This repository houses a set of lightweight services that demonstrate the AI Rooms platform. Each service is self-contained, but they can be run together via Docker for a full-stack prototype.

## Services
- **app/** – Minimal FastAPI application that exposes room chat REST/WebSocket endpoints and a deterministic embedding worker for experimentation.
- **backend/** – Authenticated FastAPI backend featuring user/nomi/room management, embeddings CRUD, and integration-style tests backed by a SQLAlchemy store (SQLite by default).
- **frontend/** – Next.js frontend for the chat interface, room list, and user authentication.
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

## Deployment

| Option                                                          | Best for                        | Notes                                |
| :-------------------------------------------------------------- | :------------------------------ | :----------------------------------- |
| **Vercel (frontend)** + **Render / Railway (backend)**          | simplest                        | Free tiers, easy push-to-deploy      |
| **Docker Compose VPS (Hetzner / DigitalOcean / AWS Lightsail)** | full control                    | You own the box, TLS via Caddy/NGINX |
| **Kubernetes (ArgoCD / Helm)**                                  | you already run Brain-Swarm Ops | integrate it into that cluster       |

### Docker Compose VPS Deployment

For full control on your own VPS (Hetzner, DigitalOcean, AWS Lightsail):

1. **Provision a VPS** with Docker and Docker Compose installed.

2. **Clone the repo** and navigate to the project directory.

3. **Update Caddyfile**: Replace `your-domain.com` with your actual domain in `infra/Caddyfile`.

4. **Set environment variables**: Create a `.env` file or set in docker-compose.yml for secrets like `OPENAI_API_KEY`, database passwords, etc.

5. **Run the stack**:
   ```bash
   docker-compose up -d
   ```

6. **Configure DNS**: Point your domain to the VPS IP.

Caddy will automatically obtain TLS certificates from Let's Encrypt.

The stack includes Caddy for reverse proxy and TLS, all services, and monitoring.

## Contributing

1. Run the relevant `make install-*` target.
2. Implement your changes.
3. Execute `make test-app` / `make test-backend`.
4. Follow up with docker-compose testing if your changes affect container builds.

Feel free to expand the Makefile targets as the stack grows (linting, formatting, migrations, etc.).
