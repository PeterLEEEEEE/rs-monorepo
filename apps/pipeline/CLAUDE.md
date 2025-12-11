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
├── dbt/                     # dbt project
│   ├── models/              # dbt models (staging, marts)
│   ├── profiles/            # dbt profiles (dev, docker)
│   └── dbt_project.yml
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

dbt project located at `dbt/` and mounted to `/usr/local/dbt` in containers.

```bash
# Local dbt commands (from apps/pipeline/)
cd dbt
dbt debug --profiles-dir profiles --target dev
dbt run --profiles-dir profiles --target dev

# Inside Airflow container
astro dev bash
dbt run --project-dir $DBT_PROJECT_DIR --profiles-dir $DBT_PROFILES_DIR --target docker
```

DAG `dags_realestate_dbt.py` triggers dbt runs via astronomer-cosmos.

## Testing

```bash
# Validate DAG syntax
astro dev pytest tests/

# Or manually
python -c "from airflow.models import DagBag; db = DagBag(); print(db.import_errors)"
```

## dbt Models (staging 스키마)

raw 스키마의 JSONB 데이터를 파싱하여 staging 스키마의 정규화된 테이블로 변환

### 모델 목록

| Model | Description | Source | Materialization |
|-------|-------------|--------|-----------------|
| `stg_real_prices` | 실거래가 정보 | raw.real_prices | incremental |
| `stg_complexes` | 단지 기본 정보 | raw.complex_details | incremental |
| `stg_pyeongs` | 평형 정보 | raw.complex_details (pyeongs 배열) | incremental |
| `stg_articles` | 매물 정보 (최근 1개월) | raw.articles | incremental |

### stg_complexes

단지 기본 정보 파싱 (raw.complex_details → staging.stg_complexes)

| Column | Type | Description |
|--------|------|-------------|
| complex_id | TEXT | 단지 ID (PK) |
| complex_name | TEXT | 단지명 |
| complex_type | TEXT | 단지 유형 코드 (A01=아파트) |
| total_dong_count | INTEGER | 총 동 수 |
| total_household_count | INTEGER | 총 세대 수 |
| use_approve_ymd | TEXT | 사용 승인일 (YYYYMMDD) |
| latitude | NUMERIC | 위도 |
| longitude | NUMERIC | 경도 |
| min_price / max_price | BIGINT | 매매가 범위 (만원) |
| min_lease_price / max_lease_price | BIGINT | 전세가 범위 (만원) |

### stg_pyeongs

평형 정보 파싱 (raw.complex_details.payload.pyeongs 배열 → staging.stg_pyeongs)

| Column | Type | Description |
|--------|------|-------------|
| complex_id | TEXT | 단지 ID |
| pyeong_id | TEXT | 평형 ID |
| pyeong_name | TEXT | 평형명 (㎡ 기준: 81C, 102A) |
| pyeong_name2 | TEXT | 평형명 (평 기준: 24C, 31A) |
| supply_area_sqm | NUMERIC | 공급면적 (㎡) |
| exclusive_area_sqm | NUMERIC | 전용면적 (㎡) |
| exclusive_area_pyeong | NUMERIC | 전용면적 (평) |

### stg_articles

매물 정보 파싱 (raw.articles → staging.stg_articles)
- **필터**: `expire_at >= CURRENT_DATE - INTERVAL '1 month'` (최근 1개월 이내 만료 매물만)

| Column | Type | Description |
|--------|------|-------------|
| complex_id | TEXT | 단지 ID |
| article_id | TEXT | 매물 ID |
| article_name | TEXT | 매물명 (단지명) |
| building_name | TEXT | 동 이름 (예: 106동) |
| trade_type_code | TEXT | 거래 유형 (A1=매매, B1=전세, B2=월세) |
| price_text | TEXT | 가격 텍스트 (예: 34억) |
| supply_area_sqm | NUMERIC | 공급면적 (㎡) |
| exclusive_area_sqm | NUMERIC | 전용면적 (㎡) |
| floor_info | TEXT | 층 정보 (예: 4/14) |
| direction | TEXT | 향 (남향, 남동향 등) |
| realtor_name | TEXT | 중개사 이름 |
| confirm_date | TIMESTAMP | 매물 확인일 |
| expire_date | TIMESTAMP | 매물 만료일 |

### dbt 실행 명령어

```bash
# 로컬 실행 (환경변수 필요)
cd apps/pipeline/dbt
DBT_HOST=localhost DBT_PORT=5434 DBT_USER=admin DBT_PASSWORD=abc123 DBT_DBNAME=realestate \
  uv run --extra local dbt run --profiles-dir profiles --target dev

# 특정 모델만 실행
DBT_HOST=localhost DBT_PORT=5434 DBT_USER=admin DBT_PASSWORD=abc123 DBT_DBNAME=realestate \
  uv run --extra local dbt run --profiles-dir profiles --target dev --select stg_complexes stg_pyeongs
```
