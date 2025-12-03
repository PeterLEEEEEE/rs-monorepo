import logging
from typing import AsyncGenerator
from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class SQLAlchemyConnection:
    def __init__(self, db_url: str, **kwargs) -> None:
        self.db_url = db_url
        self.async_engine: AsyncEngine = create_async_engine(
            db_url,
            pool_size=kwargs.get("pool_size", 10),
            max_overflow=kwargs.get("max_overflow", 20),
            pool_recycle=kwargs.get("pool_recycle", 3600),
            pool_pre_ping=True,
        )
        self.sync_engine = create_engine(
            db_url,
            pool_pre_ping=True,
            # echo=True
        )
        self.session_factory = async_scoped_session(
            async_sessionmaker(
                self.async_engine,
                expire_on_commit=False,
                autoflush=False,
                future=True,
            ),
            scopefunc=current_task,
        )
        self.sync_session_factory = sessionmaker(
            self.sync_engine,
            expire_on_commit=False,
            autoflush=False,
            future=True,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session = self.session_factory()
        try:
            yield session
        except IntegrityError as exception:
            logger.error('Session rollback because of exception: %s', exception)
            await session.rollback()
        finally:
            await session.close()
    