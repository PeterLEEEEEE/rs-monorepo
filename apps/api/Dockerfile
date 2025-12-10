FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
ENV TZ=Asia/Seoul

WORKDIR /api

# Enable bytecode compilation(실행 성능 향상)
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev


COPY src/ src/

RUN pip install debugpy
ENV PYTHONUNBUFFERED=1
# Place executables in the environment at the front of the path
ENV PATH="/api/.venv/bin:$PATH"
ENV PYTHONPATH="/api:${PYTHONPATH}"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# CMD ["fastapi", "dev", "src/server.py", "--port", "80", "--host", "0.0.0.0", "--reload"]
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "src.server:app", "--port", "80", "--host", "0.0.0.0", "--reload"]