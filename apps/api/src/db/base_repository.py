"""Repository 베이스 클래스"""
from sqlalchemy.ext.asyncio import async_scoped_session

from .session import get_session


class BaseRepository:
    """
    모든 Repository의 베이스 클래스.

    session property를 통해 현재 request context의 세션을 제공.
    """

    @property
    def session(self) -> async_scoped_session:
        """현재 context의 scoped session 반환"""
        return get_session()
