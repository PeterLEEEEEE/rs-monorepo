# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI multi-agent real estate chatbot service using LangGraph and LangChain. Implements an orchestrator pattern to route user queries to specialized agents (Property, Market, Comparison).

**Stack**: Python 3.13+, FastAPI, LangGraph, LangChain, SQLAlchemy (async), dependency-injector, Azure OpenAI

## Common Commands

```bash
# Start all services (API, PostgreSQL, MongoDB, Redis, Langfuse)
make dc-up

# Stop and clean up containers
make clean

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

API runs at http://localhost:8000, Langfuse at http://localhost:3000

## Architecture

### Directory Structure
```
src/
├── server.py          # FastAPI app creation, lifespan, MCP integration
├── container.py       # Main DI container (AppContainer)
├── router.py          # API router aggregation
├── agents/            # Multi-agent system
│   ├── base.py        # BaseAgent ABC, AgentType enum, AgentConfig
│   ├── container.py   # AgentContainer (DI for agents)
│   ├── orchestrator/  # Routes queries to specialist agents
│   ├── property/      # Property search agent
│   ├── market/        # Market analysis agent
│   └── comparison/    # Comparison agent
├── domain/            # Domain-driven design modules
│   ├── chat/          # Chat rooms and messages (controller/service/repository/models)
│   └── user/          # User management
├── core/
│   ├── config/        # Pydantic settings, environment loading
│   ├── observability/ # Langfuse integration
│   ├── security/      # JWT authentication
│   └── mcp/           # Model Context Protocol tools
└── db/
    ├── conn.py        # SQLAlchemyConnection (async session management)
    ├── postgres/      # PostgreSQL base, checkpointer
    └── mixins/        # TimestampMixin, SoftDeleteMixin
```

### Dependency Injection Pattern

Uses `dependency-injector` library. Main container hierarchy:

```python
AppContainer
├── db (SQLAlchemyConnection)
├── llm (AzureChatOpenAI)
├── agent_container (AgentContainer)
│   ├── property_agent, market_agent, comparison_agent
│   └── orchestrator (with sub_agents injected)
├── chat_container (ChatContainer)
│   └── chat_service (with orchestrator injected)
└── user_container (UserContainer)
```

Wiring: `container.wire(packages=["src.domain", "src.agents"], modules=["src.router"])`

### Agent System

BaseAgent (`src/agents/base.py`):
- Lazy-loads LangGraph ReAct agent via `get_graph()`
- Methods: `invoke()`, `invoke_with_history()`, `stream()`
- Built-in Langfuse callback support
- A2A protocol `get_agent_card()`

OrchestratorAgent routes via tools: `call_property_agent()`, `call_market_agent()`, `call_comparison_agent()`

### Domain Layer Pattern

Each domain follows: controller -> service -> repository -> models

```python
# Controller uses DI wiring
@chat_router.post("/{room_id}/message")
@inject
async def send_message(
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"])
):
    ...
```

### Database Models

- Use `TimestampMixin` for `created_at`/`updated_at`
- Use `SoftDeleteMixin` for soft deletes (`is_deleted`, `deleted_at`)
- SQLAlchemy 2.0 style with `Mapped[]` type hints

### API Serialization

Response models use snake_case internally, converted to camelCase via `alias_generator=snake2camel`

## Configuration

Environment loaded from `.env.{APP_ENV}` (defaults to `.env.dev`)

Required variables:
- Azure OpenAI: `OPENAI_API_KEY`, `OPENAI_API_VERSION`, `OPENAI_API_BASE`, `OPENAI_DEPLOYMENT_NAME`
- PostgreSQL: `POSTGRES_DB_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- MongoDB: `MONGODB_URI`
- Redis: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- Langfuse (optional): `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`

## Key Endpoints

- `POST /api/chat/room` - Create chat room
- `POST /api/chat/room/{room_id}/message` - Send message (invokes orchestrator agent)
- `GET /api/chat/room/{room_id}` - Get chat history
- A2A protocol: `/api/a2a/*` routes for agent discovery and messaging
- MCP tools: mounted at `/mcp/v1`
