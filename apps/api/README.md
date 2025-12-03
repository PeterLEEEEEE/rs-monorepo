# API - FastAPI + LangGraph Agent

Real Estate multi-agent chatbot service.

## Stack

- Python 3.13+
- FastAPI
- LangGraph + LangChain
- SQLAlchemy (async)
- dependency-injector
- Azure OpenAI

## Structure

```
src/
├── server.py          # FastAPI app, lifespan, MCP
├── container.py       # Main DI container
├── router.py          # API router aggregation
├── agents/            # Multi-agent system
│   ├── orchestrator/  # Routes to specialist agents
│   ├── property/      # Property search
│   ├── market/        # Market analysis
│   └── comparison/    # Comparison
├── domain/            # Domain modules (chat, user)
├── core/              # Config, security, observability
└── db/                # Database connections
```

## Quick Start

### Using Docker (Recommended)

```bash
# From monorepo root
docker compose up -d api
```

### Local Development

```bash
cd apps/api

# Install dependencies
uv sync

# Set environment
cp .env.example .env.dev
# Edit .env.dev with your settings

# Run server
uv run uvicorn src.server:create_app --factory --reload --port 8000
```

## Environment Variables

```bash
# Copy example and customize
cp .env.example .env.dev
```

See `.env.example` for all available variables.

## Database

Uses shared PostgreSQL (`rs_postgres:5432/realestate`):
- Schema: `public`
- Port (host): `5434`

### Migrations

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/chat/room` | Create chat room |
| `POST /api/chat/room/{id}/message` | Send message |
| `GET /api/chat/room/{id}` | Get chat history |
| `/api/a2a/*` | A2A protocol routes |
| `/mcp/v1` | MCP tools |

## Debugging

Debugpy is enabled on port `5678` for VS Code debugging.

```json
// .vscode/launch.json
{
  "name": "Attach to API",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "localhost", "port": 5678 }
}
```
