# from redis import asyncio as aioredis
from redis.asyncio.client import Redis
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware import Middleware
from contextlib import asynccontextmanager
from fastmcp import FastMCP

from src.router import router
from src.container import AppContainer
from src.core.mcp import register_basic_tools
from src.core.config import get_config
from src.agents.a2a_server import create_a2a_router


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    config = get_config()
    redis_url = f"redis://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"
    redis = Redis.from_url(redis_url, decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="rs-cache")
    yield

def load_middleware() -> list[Middleware]:
    ...

# Create MCP server
mcp = FastMCP("Tools")
register_basic_tools(mcp)
mcp_app = mcp.http_app(path='/v1')


@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    async with app_lifespan(app):
        async with mcp_app.lifespan(app):
            yield

def create_app() -> FastAPI:
    container = AppContainer()
    app_ = FastAPI(
        title="LangGraph Realestate Agent API",
        description="FastAPI with dependency injection and A2A multi-agent support",
        lifespan=combined_lifespan,
        # middleware=load_middleware,
        debug=True
    )
    app_.mount("/mcp", mcp_app)
    # 이 부분이 의존성 주입을 활성화
    container.wire(
        packages=["src.domain", "src.agents"],  # agents 패키지 추가
        modules=["src.router"]
    )

    # A2A 멀티에이전트 라우터 등록
    agent_container = container.agent_container()
    a2a_router = create_a2a_router(
        agents={
            "orchestrator": agent_container.orchestrator(),
            "property": agent_container.property_agent(),
            "market": agent_container.market_agent(),
            "comparison": agent_container.comparison_agent(),
        }
    )
    app_.include_router(a2a_router, prefix="/api")

    app_.include_router(router, prefix="/api")
    app_.container = container
    return app_ 


app = create_app()


