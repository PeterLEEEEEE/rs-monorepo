"""통합 테스트용 Container"""
from dependency_injector import containers, providers
from fakeredis import aioredis as fakeredis

from src.db.conn import SQLAlchemyConnection
from src.domain.user.container import UserContainer
from src.domain.auth.container import AuthContainer
from src.domain.auth.repository import RefreshTokenRepository


def get_test_db_url() -> str:
    """테스트 DB URL (테스트 전용 DB)"""
    return "postgresql+asyncpg://admin:abc123@localhost:5434/realestate_test"


def get_fake_redis():
    """FakeRedis 인스턴스 생성"""
    return fakeredis.FakeRedis(decode_responses=True)


class TestContainer(containers.DeclarativeContainer):
    """통합 테스트용 DI Container"""

    wiring_config = containers.WiringConfiguration(
        packages=["src"],
    )

    # 테스트 DB 연결
    db = providers.Singleton(
        SQLAlchemyConnection,
        db_url=get_test_db_url(),
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
    )

    # FakeRedis (실제 Redis 대신)
    redis_client = providers.Singleton(get_fake_redis)

    # User Container
    user_container = providers.Container(
        UserContainer,
        session_factory=db.provided.session,
    )

    # Auth Container (refresh_token_repository 포함)
    auth_container = providers.Container(
        AuthContainer,
        session_factory=db.provided.session,
        redis_client=redis_client,
    )
