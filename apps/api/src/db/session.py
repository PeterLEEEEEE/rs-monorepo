"""글로벌 scoped session 관리 모듈"""
from contextvars import ContextVar, Token
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
)

# Session context - request/transaction 별로 고유 ID 저장
session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    """현재 session context ID 반환"""
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    """session context ID 설정"""
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    """session context 리셋"""
    session_context.reset(context)


# 글로벌 scoped session - init_session()에서 초기화됨
_session: Optional[async_scoped_session[AsyncSession]] = None


def get_session() -> async_scoped_session[AsyncSession]:
    """
    글로벌 scoped session 반환.
    호출 시점에 session을 가져오므로 import 순서 문제 없음.
    """
    if _session is None:
        raise RuntimeError("Session not initialized. Call init_session() first.")
    return _session


def init_session(engine: AsyncEngine) -> async_scoped_session[AsyncSession]:
    """
    글로벌 scoped session 초기화.
    앱 시작 시 호출해야 함.
    """
    global _session

    _session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    _session = async_scoped_session(
        session_factory=_session_factory,
        scopefunc=get_session_context,
    )

    return _session
