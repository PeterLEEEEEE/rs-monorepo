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
            "/api/auth/login",
            json={"email": user.email, "password": "password123"}
        )

        # Then: 토큰 발급
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == user.email

    async def test_login_user_not_found(self, client):
        """존재하지 않는 사용자 로그인"""
        response = await client.post(
            "/api/auth/login",
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
            "/api/auth/login",
            json={"email": user.email, "password": "wrongpassword"}
        )

        assert response.status_code == 401

    async def test_login_inactive_user(self, client, db_session):
        """비활성화된 사용자 로그인"""
        user = InactiveUserFactory.build()
        db_session.add(user)
        await db_session.commit()

        response = await client.post(
            "/api/auth/login",
            json={"email": user.email, "password": "password123"}
        )

        assert response.status_code == 401


class TestAuthMe:
    """현재 사용자 조회 API 테스트"""

    async def test_get_me_success(self, authenticated_client):
        """인증된 사용자 정보 조회"""
        client, user, _ = authenticated_client

        response = await client.get("/api/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert data["username"] == user.username

    async def test_get_me_no_token(self, client):
        """토큰 없이 조회 시 401"""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401
        assert "인증 토큰이 필요합니다" in response.json()["detail"]

    async def test_get_me_invalid_token(self, client):
        """유효하지 않은 토큰"""
        client.headers["Authorization"] = "Bearer invalid.token.here"

        response = await client.get("/api/auth/me")

        assert response.status_code == 401


class TestAuthLogout:
    """로그아웃 API 테스트"""

    async def test_logout_success(self, authenticated_client):
        """로그아웃 성공"""
        client, user, refresh_token = authenticated_client

        response = await client.post(
            "/api/auth/logout",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        assert "로그아웃" in response.json()["message"]

    async def test_logout_token_blacklisted(self, authenticated_client):
        """로그아웃 후 Access Token 블랙리스트 확인"""
        client, user, refresh_token = authenticated_client

        # 로그아웃
        await client.post(
            "/api/auth/logout",
            json={"refresh_token": refresh_token}
        )

        # 같은 Access Token으로 다시 요청
        response = await client.get("/api/auth/me")

        assert response.status_code == 401
        assert "로그아웃된 토큰" in response.json()["detail"]

    async def test_logout_refresh_token_deleted(self, authenticated_client):
        """로그아웃 후 Refresh Token으로 갱신 실패 확인"""
        client, user, refresh_token = authenticated_client

        # 로그아웃
        await client.post(
            "/api/auth/logout",
            json={"refresh_token": refresh_token}
        )

        # 삭제된 Refresh Token으로 갱신 시도
        # 새 클라이언트로 요청 (Authorization 헤더 없이)
        client.headers.pop("Authorization", None)
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )

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
            "/api/auth/login",
            json={"email": user.email, "password": "password123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # 토큰 갱신
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_token_invalid(self, client):
        """유효하지 않은 refresh token"""
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid.refresh.token"}
        )

        assert response.status_code == 401
