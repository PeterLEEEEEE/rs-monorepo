# RS Monorepo

Real Estate Agent Platform - Monorepo

## Structure

```
rs-monorepo/
├── apps/
│   ├── api/          # FastAPI backend (Agent, Auth, Chat)
│   ├── web/          # Next.js frontend
│   └── pipeline/     # Airflow data pipeline (ELT)
├── packages/
│   └── shared-types/ # Shared TypeScript types
└── .github/
    └── workflows/    # CI/CD per app
```

## Quick Start

```bash
# Start all services
docker compose up -d

# Or start individually
docker compose up api -d
docker compose up web -d
```

## Development

Each app has its own README with specific instructions:

- [API](./apps/api/README.md)
- [Web](./apps/web/README.md)
- [Pipeline](./apps/pipeline/README.md)
