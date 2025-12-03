# syntax=docker/dockerfile:1.7-labs
FROM astrocrpublic.azurecr.io/runtime:3.1-2-python-3.12

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
ENV PATH="/root/.local/bin:${PATH}"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && { [ -e /usr/local/bin/uv ] || ln -s /root/.local/bin/uv /usr/local/bin/uv; } \
 && { [ -e /usr/local/bin/uvx ] || ln -s /root/.local/bin/uvx /usr/local/bin/uvx; }

WORKDIR /usr/local/airflow

# pyproject.toml에서 requirements.txt 생성 후 설치
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system -r requirements.txt

# dbt 설치
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system dbt-core dbt-postgres astronomer-cosmos

# dbt 프로젝트 경로 설정
ENV DBT_PROJECT_DIR=/usr/local/dbt
ENV DBT_PROFILES_DIR=/usr/local/dbt/profiles

USER astro
