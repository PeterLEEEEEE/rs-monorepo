# RS Monorepo

Real Estate Agent Platform - Monorepo

## Structure

```
rs/
├── docker/               # Shared infrastructure
│   ├── postgres/         # PostgreSQL (PostGIS + pgvector)
│   ├── mongo/            # MongoDB
│   └── redis/            # Redis
├── apps/
│   ├── api/              # FastAPI backend (Agent, Auth, Chat)
│   ├── pipeline/         # Airflow data pipeline (ELT) + dbt
│   └── web/              # React frontend
├── packages/
│   └── shared-types/     # Shared TypeScript types (planned)
├── .github/
│   └── workflows/        # CI/CD per app
└── docker-compose.yml    # All services orchestration
```

## Prerequisites

- Docker & Docker Compose
- [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) (for Pipeline)

## Quick Start

### 1. Start All Services

```bash
# Start all services (postgres, mongo, redis, api, web, langfuse)
docker compose up -d

# Or start specific services
docker compose up -d postgres mongo redis  # Infrastructure only
docker compose up -d api                    # API only
docker compose up -d web                    # Web only
```

### 2. Start Pipeline (Airflow)

```bash
cd apps/pipeline
astro dev start
```

### After Reboot

```bash
# 1. Start services
cd /path/to/rs
docker compose up -d

# 2. Start Pipeline (Airflow)
cd apps/pipeline
astro dev start
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI backend |
| Airflow | http://localhost:8080 | Airflow UI |
| Web | http://localhost:80 | React frontend |
| Langfuse | http://localhost:3000 | LLM observability |

## Ports

| Port | Service |
|------|---------|
| 5434 | PostgreSQL (PostGIS + pgvector) |
| 27017 | MongoDB |
| 6379 | Redis |
| 5432 | Airflow internal PostgreSQL |
| 8000 | API |
| 8080 | Airflow UI |
| 80 | Web |
| 3000 | Langfuse |

## Database

단일 PostgreSQL (`rs_postgres`)을 API와 Pipeline이 공유하며, 스키마로 분리:

- `public`: API 데이터
- `staging`: dbt staging models
- `marts`: dbt mart models

```bash
# Connection info
Host: localhost
Port: 5434
Database: realestate
User: admin
Password: (see .env)
```

## Development

Each app has its own README with specific instructions:

- [API](./apps/api/README.md) - FastAPI + LangGraph Agent
- [Pipeline](./apps/pipeline/README.md) - Airflow + dbt
- [Web](./apps/web/README.md) - React + Vite

## Environment Variables

```bash
# Copy example and customize
cp .env.example .env
```

See `.env.example` for available variables.
