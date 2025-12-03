# CLAUDE.md

This file provides guidance to Claude Code when working with the pipeline app.

## Project Overview

Airflow-based data pipeline for real estate data collection and transformation (ELT). Built with Astronomer CLI.

**Stack**: Python 3.12+, Apache Airflow, dbt, PostgreSQL, Astronomer

## Common Commands

```bash
# Start Airflow locally (Astronomer CLI)
astro dev start

# Stop Airflow
astro dev stop

# Restart after DAG changes
astro dev restart

# View logs
astro dev logs

# Access Airflow shell
astro dev bash
```

Airflow UI: http://localhost:8080 (admin/admin)

## Directory Structure

```
apps/pipeline/
├── dags/                    # Airflow DAG definitions
│   ├── dags_realestate_api.py   # Real estate API data collection
│   ├── dags_realestate_dbt.py   # dbt transformation
│   ├── dags_dong_init.py        # 동(neighborhood) initialization
│   ├── dags_region_init.py      # Region initialization
│   └── common_tasks.py          # Shared task utilities
├── src/                     # Python modules for DAGs
├── plugins/                 # Custom Airflow plugins
├── docker/                  # Docker configurations
│   └── postgres/            # PostgreSQL init scripts
├── tests/                   # DAG and integration tests
├── Dockerfile               # Astronomer runtime image
└── docker-compose.override.yml  # Local dev overrides
```

## DAG Patterns

### TaskFlow API (Preferred)
```python
from airflow.decorators import dag, task

@dag(schedule="@daily", catchup=False)
def my_dag():
    @task
    def extract():
        return data

    @task
    def transform(data):
        return transformed

    transform(extract())
```

### Common Tasks
Import shared utilities from `dags/common_tasks.py`

## Database

- **Airflow metadata**: Internal PostgreSQL (managed by Astronomer)
- **Application data**: External PostgreSQL (`postgres_stg_db` on port 5434)

## dbt Integration

dbt project mounted at `/usr/local/rs_dbt`. DAG `dags_realestate_dbt.py` triggers dbt runs.

## Testing

```bash
# Validate DAG syntax
astro dev pytest tests/

# Or manually
python -c "from airflow.models import DagBag; db = DagBag(); print(db.import_errors)"
```
