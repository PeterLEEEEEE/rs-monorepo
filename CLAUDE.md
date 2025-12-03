# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real Estate Agent Platform - Monorepo containing:
- **API** (`apps/api/`): FastAPI multi-agent chatbot service
- **Pipeline** (`apps/pipeline/`): Airflow data pipeline (ELT)
- **Web** (`apps/web/`): Frontend (planned - Next.js)

## Monorepo Structure

```
rs-monorepo/
├── apps/
│   ├── api/          # FastAPI, LangGraph, LangChain
│   ├── pipeline/     # Airflow, dbt
│   └── web/          # Next.js (planned)
├── packages/
│   └── shared-types/ # Shared TypeScript types
├── .github/
│   └── workflows/    # CI/CD per app (path-filtered)
└── docker-compose.yml
```

## Common Commands

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up api -d
docker compose up postgres redis mongo -d

# Stop all
docker compose down
```

## Per-App Details

Each app has its own CLAUDE.md with specific guidance:
- `apps/api/CLAUDE.md` - Agent system, DI pattern, domain structure
- `apps/pipeline/CLAUDE.md` - DAG patterns, ELT workflows

## Shared Infrastructure

### Docker Services
| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | FastAPI backend |
| PostgreSQL | 5432 | Main database |
| MongoDB | 27017 | Document storage |
| Redis | 6379 | Cache, checkpoints |
| Langfuse | 3000 | LLM observability |

### Network
All services use `realestate_network` for inter-container communication.

## CI/CD

GitHub Actions workflows are path-filtered:
- `.github/workflows/api.yml` - Runs only when `apps/api/**` changes
- `.github/workflows/pipeline.yml` - Runs only when `apps/pipeline/**` changes

## Development Guidelines

1. **Changes affecting multiple apps**: Create separate commits per app for cleaner history
2. **Shared types**: Add to `packages/shared-types/` when frontend is added
3. **Environment files**: Each app has its own `.env.dev` in its directory
