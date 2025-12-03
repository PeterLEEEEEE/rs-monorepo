# Pipeline - Airflow + dbt

Real estate data pipeline for collection and transformation (ELT).

## Stack

- Python 3.12
- Apache Airflow 3.x (Astronomer Runtime)
- dbt-core + dbt-postgres
- astronomer-cosmos
- PostgreSQL (PostGIS + pgvector)

## Structure

```
apps/pipeline/
├── dags/                    # Airflow DAG definitions
│   ├── dags_realestate_api.py   # API data collection
│   ├── dags_realestate_dbt.py   # dbt transformation
│   ├── dags_region_init.py      # Region initialization
│   └── common_tasks.py          # Shared utilities
├── dbt/                     # dbt project
│   ├── models/
│   │   ├── staging/         # Bronze → Silver
│   │   └── marts/           # Silver → Gold
│   ├── profiles/            # Connection profiles
│   └── dbt_project.yml
├── src/                     # Python modules for DAGs
├── plugins/                 # Custom Airflow plugins
├── Dockerfile               # Astronomer runtime image
└── docker-compose.override.yml
```

## Quick Start

### Prerequisites

- [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli)
- Docker

### Start Airflow

```bash
cd apps/pipeline

# Start Airflow (spins up 5 containers)
astro dev start

# Stop Airflow
astro dev stop

# Restart after changes
astro dev restart

# View logs
astro dev logs

# Access Airflow shell
astro dev bash
```

**Airflow UI**: http://localhost:8080

### After Reboot

```bash
# 1. Start infrastructure first (from monorepo root)
cd /path/to/rs
docker compose up -d

# 2. Start Airflow
cd apps/pipeline
astro dev start
```

## Database

Uses shared PostgreSQL (`rs_postgres`):

| Setting | Value |
|---------|-------|
| Host (container) | `rs_postgres` |
| Host (local) | `localhost` |
| Port (container) | `5432` |
| Port (local) | `5434` |
| Database | `realestate` |
| User | `admin` |
| Password | (see .env) |

### Schemas

- `staging`: dbt staging models (incremental)
- `marts`: dbt mart models (tables)

## dbt

### Local Development

```bash
cd apps/pipeline/dbt

# Test connection
dbt debug --profiles-dir profiles --target dev

# Run models
dbt run --profiles-dir profiles --target dev

# Run specific model
dbt run --profiles-dir profiles --target dev --select staging.stg_apartments
```

### Inside Airflow Container

```bash
# Enter container
astro dev bash

# Run dbt
dbt run --project-dir $DBT_PROJECT_DIR --profiles-dir $DBT_PROFILES_DIR --target docker
```

### Profiles

`dbt/profiles/profiles.yml` has two targets:

- `dev`: Local development (localhost:5434)
- `docker`: Inside Airflow container (rs_postgres:5432)

**Note**: dbt uses environment variables for credentials. Set `DBT_PASSWORD` before running.

## DAGs

| DAG | Description |
|-----|-------------|
| `dags_realestate_api_to_postgres` | Collect data from Naver API |
| `dags_realestate_dbt` | Run dbt transformations |
| `dags_region_init_yearly` | Initialize region data |

## Testing

```bash
# Validate DAG syntax
astro dev pytest tests/

# Or manually
python -c "from airflow.models import DagBag; db = DagBag(); print(db.import_errors)"
```

## Network

Airflow containers connect to `realestate_network` to access:
- `rs_postgres` - Main PostgreSQL
- `rs_mongo` - MongoDB
- `rs_redis` - Redis

This is configured in `docker-compose.override.yml`.
