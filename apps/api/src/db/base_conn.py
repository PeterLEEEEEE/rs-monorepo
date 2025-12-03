from fastapi import FastAPI
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing_extensions import AsyncGenerator


meta = MetaData()
Base = declarative_base()


class SQLAlchemyClient:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine: None = None
        self._session: None = None
        if app is not None:
            self.init_app(app=app, **kwargs)
    
    def init_app(self, app: FastAPI, **kwargs):
        """
        DB 초기화 함수
        :param app: FastAPI 인스턴스
        :param kwargs:
        :return:
        """
        database_url = kwargs.get("DB_URL")
        pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900)
        test_mode = kwargs.setdefault("TEST_MODE", False)
        echo = kwargs.setdefault("DB_ECHO", True)

        if test_mode:
            ...
        
        self._engine = create_async_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )
        
        self._session = async_sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
        
    @property
    async def session(self):
        return await self.get_db

    @property
    def engine(self):
        return self._engine

    async def get_db(self) -> AsyncGenerator[AsyncSession]:
        async with self._engine.begin() as conn:
            await conn.run_sync(meta.create_all)
        
        db_session = None
        try:
            db_session = self._session()
            yield db_session
        finally:
            await db_session.close()


db_client = SQLAlchemyClient()
