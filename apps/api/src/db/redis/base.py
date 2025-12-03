from typing import Protocol, Any
from abc import ABC, abstractmethod


class BaseService(Protocol):

    async def get(self, key: str) -> Any:
        """Retrieve a value from the cache by key."""
        pass

    async def set(self, key: str, value: Any, expire: int = 0) -> None:
        """Set a value in the cache with an optional expiration time."""
        pass


    async def delete_startswith(self, key: str) -> None:
        """Delete a value from the cache by key."""
        pass


    async def clear(self) -> None:
        """Clear the entire cache."""
        pass

class BaseKeyBuilder(Protocol):

    def build(self, func: Any, *args: Any, **kwargs: Any) -> str:
        """Generate a cache key based on the function and its arguments."""
        pass