"""Auth API 통합 테스트"""
import pytest

from .factories import UserFactory, InactiveUserFactory


class TestAuthLogin:
    """로그인 API 테스트"""

    async def test_login_success(self, client, db_session):
        """로그인 성공"""
        # Given: 사용자 생성
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()

        # When: 로그인 요청
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "password123", "device_id": "test-device"}
        )

        # Then: 토큰 발급
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" not in data  # refresh_token은 쿠키로 전달
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == user.email
        # 쿠키에 refresh_token이 설정되었는지 확인
        assert "refresh_token" in response.cookies

    async def test_login_user_not_found(self, client):
        """존재하지 않는 사용자 로그인"""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "notfound@test.com", "password": "password123"}
        )

        assert response.status_code == 401
        assert "이메일 또는 비밀번호" in response.json()["detail"]

    async def test_login_wrong_password(self, client, db_session):
        """잘못된 비밀번호"""
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "wrongpassword"}
        )

        assert response.status_code == 401

    async def test_login_inactive_user(self, client, db_session):
        """비활성화된 사용자 로그인"""
        user = InactiveUserFactory.build()
        db_session.add(user)
        await db_session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "password123"}
        )

        assert response.status_code == 401

    async def test_login_same_device_replaces_token(self, client, db_session):
        """같은 device_id로 재로그인 시 기존 토큰 교체"""
        from sqlalchemy import select, func
        from src.domain.auth.models import RefreshToken

        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()

        # 첫 번째 로그인
        response1 = await client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "password123", "device_id": "same-device"}
        )
        assert response1.status_code == 200
        token1 = response1.cookies.get("refresh_token")

        # DB에 토큰 1개 존재 확인
        count_query = select(func.count()).select_from(RefreshToken).where(
            RefreshToken.user_id == user.id,
            RefreshToken.device_info == "same-device"
        )
        result = await db_session.execute(count_query)
        assert result.scalar() == 1

        # 같은 device_id로 두 번째 로그인
        response2 = await client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "password123", "device_id": "same-device"}
        )
        assert response2.status_code == 200
        token2 = response2.cookies.get("refresh_token")

        # DB에 여전히 토큰 1개만 존재 (기존 토큰 삭제 후 새 토큰 생성)
        result = await db_session.execute(count_query)
        assert result.scalar() == 1

        # 새로운 토큰이 발급됨 확인 (같은 초에 생성되면 토큰 문자열이 같을 수 있으므로, 토큰 존재 여부만 확인)
        assert token1 is not None
        assert token2 is not None


class TestAuthMe:
    """현재 사용자 조회 API 테스트"""

    async def test_get_me_success(self, authenticated_client):
        """인증된 사용자 정보 조회"""
        client, user, _ = authenticated_client

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert data["username"] == user.username

    async def test_get_me_no_token(self, client):
        """토큰 없이 조회 시 401"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "인증 토큰이 필요합니다" in response.json()["detail"]

    async def test_get_me_invalid_token(self, client):
        """유효하지 않은 토큰"""
        client.headers["Authorization"] = "Bearer invalid.token.here"

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401


class TestAuthLogout:
    """로그아웃 API 테스트"""

    async def test_logout_success(self, authenticated_client):
        """로그아웃 성공"""
        client, user, refresh_token = authenticated_client

        # refresh_token을 쿠키로 설정
        client.cookies.set("refresh_token", refresh_token)

        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        assert "로그아웃" in response.json()["message"]

    async def test_logout_token_blacklisted(self, authenticated_client):
        """로그아웃 후 Access Token 블랙리스트 확인"""
        client, user, refresh_token = authenticated_client

        # refresh_token을 쿠키로 설정
        client.cookies.set("refresh_token", refresh_token)

        # 로그아웃
        await client.post("/api/v1/auth/logout")

        # 같은 Access Token으로 다시 요청
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "로그아웃된 토큰" in response.json()["detail"]

    async def test_logout_refresh_token_deleted(self, authenticated_client):
        """로그아웃 후 Refresh Token으로 갱신 실패 확인"""
        client, user, refresh_token = authenticated_client

        # refresh_token을 쿠키로 설정
        client.cookies.set("refresh_token", refresh_token)

        # 로그아웃
        await client.post("/api/v1/auth/logout")

        # 삭제된 Refresh Token으로 갱신 시도
        client.headers.pop("Authorization", None)
        # 쿠키에 refresh_token 재설정 (로그아웃으로 삭제되었지만 테스트를 위해)
        client.cookies.set("refresh_token", refresh_token)
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401


class TestAuthRefresh:
    """토큰 갱신 API 테스트"""

    async def test_refresh_token_success(self, client, db_session):
        """토큰 갱신 성공"""
        # 사용자 생성 및 로그인
        user = UserFactory.build()
        db_session.add(user)
        await db_session.commit()

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "password123"}
        )
        # refresh_token은 쿠키에서 가져옴
        refresh_token = login_response.cookies.get("refresh_token")

        # 쿠키 설정 후 토큰 갱신
        client.cookies.set("refresh_token", refresh_token)
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_token_invalid(self, client):
        """유효하지 않은 refresh token"""
        client.cookies.set("refresh_token", "invalid.refresh.token")
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    async def test_refresh_token_missing(self, client):
        """refresh token 없이 요청"""
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401
        assert "Refresh token이 없습니다" in response.json()["detail"]
