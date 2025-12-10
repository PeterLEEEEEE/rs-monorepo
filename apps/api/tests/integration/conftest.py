"""통합 테스트 Fixtures"""
import pytest
import os

# 테스트 환경변수 설정 (import 전에 설정해야 함)
os.environ["APP_ENV"] = "dev"  # .env.dev 사용

from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from src.domain.user.models import User
from src.db.postgres.conn import Base

from .container import TestContainer
from .factories import UserFactory


@pytest.fixture(scope="function")
def test_container():
    """테스트용 Container"""
    container = TestContainer()
    container.wire(packages=["src"])
    yield container
    container.unwire()


@pytest.fixture(scope="function")
async def db_session(test_container):
    """테스트별 DB 세션 (트랜잭션 롤백)"""
    db = test_container.db()
    async with db.session() as session:
        yield session
        # 테스트 후 롤백
        await session.rollback()


@pytest.fixture(scope="function")
async def setup_database(test_container):
    """테스트 DB 테이블 생성 및 정리"""
    db = test_container.db()

    # 테이블 생성 (이미 있으면 무시)
    async with db.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # 테스트 후 데이터 정리 (테이블은 유지, 데이터만 삭제)
    async with db.async_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def app(test_container, setup_database):
    """테스트용 FastAPI 앱"""
    from src.server import create_app

    app = create_app()

    # Container override - auth_container와 user_container만 교체
    app.container.auth_container.override(test_container.auth_container)
    app.container.user_container.override(test_container.user_container)
    app.container.redis_client.override(test_container.redis_client)

    yield app

    # Override 해제
    app.container.auth_container.reset_override()
    app.container.user_container.reset_override()
    app.container.redis_client.reset_override()


@pytest.fixture
async def client(app):
    """비동기 테스트 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def authenticated_client(client, test_container, db_session):
    """인증된 테스트 클라이언트"""
    # 테스트 유저 생성
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 로그인해서 토큰 발급
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123", "device_id": "test-device"}
    )

    refresh_token = None
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        # refresh_token은 쿠키에서 가져옴
        refresh_token = response.cookies.get("refresh_token")
        client.headers["Authorization"] = f"Bearer {token}"

    # client, user, refresh_token 반환
    yield client, user, refresh_token

    # 정리
    await db_session.delete(user)
    await db_session.commit()


@pytest.fixture
def user_factory():
    """UserFactory 접근용"""
    return UserFactory
