from typing_extensions import Any

from redis.asyncio import Redis
from dependency_injector.providers import Singleton
from dependency_injector.wiring import Provide

from .base import BaseService


class RedisService(BaseService):
    redis_provider: Singleton[Redis] = Provide["redis.provider"]

    async def get(self, key: str) -> Any:
        ...
    
    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        ...
    
    async def delete(self, key: str) -> None:
        ...

# class RedisService(BaseService):
    
#     async def get(self, *, key: str) -> Any:
#         result = await 