"""AuthService 유닛 테스트"""
import pytest
from unittest.mock import AsyncMock

from src.domain.auth.service import AuthService, BLACKLIST_PREFIX
from src.domain.user.service import hash_password


class MockUser:
    """테스트용 User Mock 객체"""

    def __init__(
        self,
        id: int = 1,
        email: str = "test@test.com",
        username: str = "testuser",
        hashed_password: str = None,
        role: str = "USER",
        is_active: bool = True,
    ):
        self.id = id
        self.email = email
        self.username = username
        self.hashed_password = hashed_password or hash_password("password123")
        self.role = role
        self.is_active = is_active


@pytest.fixture
def mock_user_repository():
    """Mock UserRepository"""
    return AsyncMock()


@pytest.fixture
def mock_refresh_token_repository():
    """Mock RefreshTokenRepository"""
    return AsyncMock()


@pytest.fixture
def mock_redis_client():
    """Mock Redis Client"""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_repository, mock_refresh_token_repository, mock_redis_client):
    """AuthService 인스턴스"""
    return AuthService(
        user_repository=mock_user_repository,
        refresh_token_repository=mock_refresh_token_repository,
        redis_client=mock_redis_client,
    )


@pytest.fixture
def mock_user():
    """테스트용 사용자"""
    return MockUser()


class TestAuthServiceLogin:
    """로그인 테스트"""

    async def test_login_success(self, auth_service, mock_user_repository, mock_refresh_token_repository, mock_user):
        """로그인 성공"""
        mock_user_repository.get_by_email.return_value = mock_user
        mock_refresh_token_repository.delete_by_user_and_device.return_value = 0

        result = await auth_service.login("test@test.com", "password123", device_id="test-device", ip_address="127.0.0.1")

        assert result is not None
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        assert result.user.id == mock_user.id
        assert result.user.email == mock_user.email
        mock_user_repository.get_by_email.assert_called_once_with("test@test.com")
        mock_refresh_token_repository.create.assert_called_once()

    async def test_login_user_not_found(self, auth_service, mock_user_repository):
        """존재하지 않는 사용자 로그인 실패"""
        mock_user_repository.get_by_email.return_value = None

        result = await auth_service.login("notfound@test.com", "password123")

        assert result is None

    async def test_login_wrong_password(self, auth_service, mock_user_repository, mock_user):
        """잘못된 비밀번호로 로그인 실패"""
        mock_user_repository.get_by_email.return_value = mock_user

        result = await auth_service.login("test@test.com", "wrongpassword")

        assert result is None

    async def test_login_inactive_user(self, auth_service, mock_user_repository):
        """비활성화된 사용자 로그인 실패"""
        inactive_user = MockUser(is_active=False)
        mock_user_repository.get_by_email.return_value = inactive_user

        result = await auth_service.login("test@test.com", "password123")

        assert result is None

    async def test_login_same_device_deletes_old_token(self, auth_service, mock_user_repository, mock_refresh_token_repository, mock_user):
        """같은 device_id로 로그인 시 기존 토큰 삭제"""
        mock_user_repository.get_by_email.return_value = mock_user
        mock_refresh_token_repository.delete_by_user_and_device.return_value = 1

        result = await auth_service.login("test@test.com", "password123", device_id="same-device")

        assert result is not None
        mock_refresh_token_repository.delete_by_user_and_device.assert_called_once_with(mock_user.id, "same-device")


class MockRefreshToken:
    """테스트용 RefreshToken Mock 객체"""

    def __init__(self, user_id: int, token: str, expires_at=None):
        from datetime import datetime, timedelta, timezone
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at or (datetime.now(timezone.utc) + timedelta(days=7))
        self.created_at = datetime.now(timezone.utc)


class TestAuthServiceRefreshToken:
    """토큰 갱신 테스트"""

    async def test_refresh_token_success(
        self, auth_service, mock_user_repository, mock_refresh_token_repository, mock_user
    ):
        """토큰 갱신 성공"""
        from src.core.security.jwt import jwt_handler

        refresh_token = jwt_handler.create_refresh_token(user_id=mock_user.id)
        mock_stored_token = MockRefreshToken(user_id=mock_user.id, token=refresh_token)

        mock_refresh_token_repository.get_by_token.return_value = mock_stored_token
        mock_user_repository.get_by_id.return_value = mock_user

        result = await auth_service.refresh_access_token(refresh_token)

        assert result is not None
        assert result.access_token is not None
        assert result.token_type == "bearer"
        mock_refresh_token_repository.get_by_token.assert_called_once_with(refresh_token)

    async def test_refresh_token_not_in_db(self, auth_service, mock_refresh_token_repository):
        """DB에 없는 refresh token으로 갱신 실패"""
        from src.core.security.jwt import jwt_handler

        refresh_token = jwt_handler.create_refresh_token(user_id=1)
        mock_refresh_token_repository.get_by_token.return_value = None

        result = await auth_service.refresh_access_token(refresh_token)

        assert result is None

    async def test_refresh_token_user_not_found(
        self, auth_service, mock_user_repository, mock_refresh_token_repository
    ):
        """사용자가 없을 때 토큰 갱신 실패"""
        from src.core.security.jwt import jwt_handler

        refresh_token = jwt_handler.create_refresh_token(user_id=999)
        mock_stored_token = MockRefreshToken(user_id=999, token=refresh_token)

        mock_refresh_token_repository.get_by_token.return_value = mock_stored_token
        mock_user_repository.get_by_id.return_value = None

        result = await auth_service.refresh_access_token(refresh_token)

        assert result is None

    async def test_refresh_token_inactive_user(
        self, auth_service, mock_user_repository, mock_refresh_token_repository
    ):
        """비활성화된 사용자 토큰 갱신 실패"""
        from src.core.security.jwt import jwt_handler

        inactive_user = MockUser(is_active=False)
        refresh_token = jwt_handler.create_refresh_token(user_id=inactive_user.id)
        mock_stored_token = MockRefreshToken(user_id=inactive_user.id, token=refresh_token)

        mock_refresh_token_repository.get_by_token.return_value = mock_stored_token
        mock_user_repository.get_by_id.return_value = inactive_user

        result = await auth_service.refresh_access_token(refresh_token)

        assert result is None

    async def test_refresh_token_expired_in_db(
        self, auth_service, mock_refresh_token_repository
    ):
        """DB에서 만료된 토큰으로 갱신 실패"""
        from datetime import datetime, timedelta, timezone
        from src.core.security.jwt import jwt_handler

        refresh_token = jwt_handler.create_refresh_token(user_id=1)
        expired_stored_token = MockRefreshToken(
            user_id=1,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # 이미 만료
        )

        mock_refresh_token_repository.get_by_token.return_value = expired_stored_token

        result = await auth_service.refresh_access_token(refresh_token)

        assert result is None
        # 만료된 토큰은 DB에서 삭제
        mock_refresh_token_repository.delete_by_token.assert_called_once_with(refresh_token)

    async def test_refresh_token_invalid_token(self, auth_service):
        """유효하지 않은 refresh token으로 갱신 실패"""
        result = await auth_service.refresh_access_token("invalid.token.here")

        assert result is None

    async def test_refresh_token_with_access_token_fails(self, auth_service, mock_user):
        """access token으로 갱신 시도 실패"""
        from src.core.security.jwt import jwt_handler

        access_token = jwt_handler.create_access_token(
            user_id=mock_user.id,
            email=mock_user.email,
        )

        result = await auth_service.refresh_access_token(access_token)

        assert result is None


class TestAuthServiceBlacklist:
    """토큰 블랙리스트 테스트"""

    async def test_add_token_to_blacklist_success(self, auth_service, mock_redis_client):
        """토큰 블랙리스트 추가 성공"""
        from src.core.security.jwt import jwt_handler

        token = jwt_handler.create_access_token(
            user_id=1,
            email="test@test.com",
        )

        result = await auth_service.add_token_to_blacklist(token)

        assert result is True
        mock_redis_client.setex.assert_called_once()

        # setex 호출 인자 확인
        call_args = mock_redis_client.setex.call_args
        key = call_args[0][0]
        assert key.startswith(BLACKLIST_PREFIX)
        assert token in key

    async def test_add_invalid_token_to_blacklist(self, auth_service, mock_redis_client):
        """유효하지 않은 토큰 블랙리스트 추가 (무시됨)"""
        result = await auth_service.add_token_to_blacklist("invalid.token")

        assert result is True
        mock_redis_client.setex.assert_not_called()

    async def test_add_token_to_blacklist_redis_error(self, auth_service, mock_redis_client):
        """Redis 에러 시 블랙리스트 추가 실패"""
        from src.core.security.jwt import jwt_handler

        token = jwt_handler.create_access_token(
            user_id=1,
            email="test@test.com",
        )
        mock_redis_client.setex.side_effect = Exception("Redis connection error")

        result = await auth_service.add_token_to_blacklist(token)

        assert result is False

    async def test_is_token_blacklisted_true(self, auth_service, mock_redis_client):
        """블랙리스트에 있는 토큰 확인"""
        mock_redis_client.get.return_value = "blacklisted"

        result = await auth_service.is_token_blacklisted("some.token.here")

        assert result is True
        mock_redis_client.get.assert_called_once()

    async def test_is_token_blacklisted_false(self, auth_service, mock_redis_client):
        """블랙리스트에 없는 토큰 확인"""
        mock_redis_client.get.return_value = None

        result = await auth_service.is_token_blacklisted("some.token.here")

        assert result is False

    async def test_is_token_blacklisted_redis_error(self, auth_service, mock_redis_client):
        """Redis 에러 시 블랙리스트 확인 실패 (False 반환)"""
        mock_redis_client.get.side_effect = Exception("Redis connection error")

        result = await auth_service.is_token_blacklisted("some.token.here")

        assert result is False


class TestAuthServiceGetUser:
    """사용자 조회 테스트"""

    async def test_get_user_by_id_success(self, auth_service, mock_user_repository, mock_user):
        """사용자 ID로 조회 성공"""
        mock_user_repository.get_by_id.return_value = mock_user

        result = await auth_service.get_user_by_id(1)

        assert result is not None
        assert result.id == mock_user.id
        mock_user_repository.get_by_id.assert_called_once_with(1)

    async def test_get_user_by_id_not_found(self, auth_service, mock_user_repository):
        """존재하지 않는 사용자 조회"""
        mock_user_repository.get_by_id.return_value = None

        result = await auth_service.get_user_by_id(999)

        assert result is None


class TestAuthServiceLogout:
    """로그아웃 테스트"""

    async def test_logout_success(
        self, auth_service, mock_redis_client, mock_refresh_token_repository
    ):
        """로그아웃 성공 - Access Token 블랙리스트 + Refresh Token DB 삭제"""
        from src.core.security.jwt import jwt_handler

        access_token = jwt_handler.create_access_token(
            user_id=1,
            email="test@test.com",
        )
        refresh_token = jwt_handler.create_refresh_token(user_id=1)

        result = await auth_service.logout(access_token, refresh_token)

        assert result is True
        mock_redis_client.setex.assert_called_once()
        mock_refresh_token_repository.delete_by_token.assert_called_once_with(refresh_token)

    async def test_logout_all_devices_success(
        self, auth_service, mock_refresh_token_repository
    ):
        """모든 기기에서 로그아웃 성공"""
        mock_refresh_token_repository.delete_by_user_id.return_value = 3

        result = await auth_service.logout_all_devices(1)

        assert result == 3
        mock_refresh_token_repository.delete_by_user_id.assert_called_once_with(1)
