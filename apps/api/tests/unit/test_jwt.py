"""JWT 토큰 생성 및 검증 유닛 테스트"""
import pytest
from datetime import datetime, timezone
from jose import jwt, ExpiredSignatureError

from src.core.security.jwt import JWTHandler, TokenType


class TestJWTHandler:
    """JWTHandler 클래스 테스트"""

    @pytest.fixture
    def jwt_handler(self, jwt_secret):
        """테스트용 JWTHandler 인스턴스"""
        return JWTHandler(
            secret_key=jwt_secret,
            algorithm="HS256",
            access_token_expire_minutes=60,
            refresh_token_expire_days=7,
        )

    # ============== Access Token 테스트 ==============

    def test_create_access_token_success(self, jwt_handler, test_user_data):
        """Access Token 생성 성공"""
        token = jwt_handler.create_access_token(
            user_id=test_user_data["id"],
            email=test_user_data["email"],
            role=test_user_data["role"],
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_contains_correct_claims(self, jwt_handler, jwt_secret, test_user_data):
        """Access Token에 올바른 클레임이 포함되어 있는지 확인"""
        token = jwt_handler.create_access_token(
            user_id=test_user_data["id"],
            email=test_user_data["email"],
            role=test_user_data["role"],
        )

        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])

        assert payload["sub"] == str(test_user_data["id"])
        assert payload["email"] == test_user_data["email"]
        assert payload["role"] == test_user_data["role"]
        assert payload["type"] == TokenType.ACCESS
        assert "iat" in payload
        assert "exp" in payload

    def test_access_token_with_additional_claims(self, jwt_handler, jwt_secret, test_user_data):
        """추가 클레임이 포함된 Access Token 생성"""
        additional = {"custom_field": "custom_value"}

        token = jwt_handler.create_access_token(
            user_id=test_user_data["id"],
            email=test_user_data["email"],
            additional_claims=additional,
        )

        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])

        assert payload["custom_field"] == "custom_value"

    def test_verify_access_token_success(self, jwt_handler, test_user_data):
        """Access Token 검증 성공"""
        token = jwt_handler.create_access_token(
            user_id=test_user_data["id"],
            email=test_user_data["email"],
            role=test_user_data["role"],
        )

        payload = jwt_handler.verify_access_token(token)

        assert payload["sub"] == str(test_user_data["id"])
        assert payload["email"] == test_user_data["email"]
        assert payload["type"] == TokenType.ACCESS

    def test_verify_access_token_with_refresh_token_fails(self, jwt_handler, test_user_data):
        """Refresh Token으로 Access Token 검증 시 실패"""
        refresh_token = jwt_handler.create_refresh_token(user_id=test_user_data["id"])

        with pytest.raises(ValueError, match="expected access token"):
            jwt_handler.verify_access_token(refresh_token)

    def test_verify_access_token_invalid_token(self, jwt_handler):
        """유효하지 않은 토큰 검증 실패"""
        from jose import JWTError

        with pytest.raises(JWTError):
            jwt_handler.verify_access_token("invalid.token.here")

    # ============== Refresh Token 테스트 ==============

    def test_create_refresh_token_success(self, jwt_handler, test_user_data):
        """Refresh Token 생성 성공"""
        token = jwt_handler.create_refresh_token(user_id=test_user_data["id"])

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_refresh_token_contains_correct_claims(self, jwt_handler, jwt_secret, test_user_data):
        """Refresh Token에 올바른 클레임이 포함되어 있는지 확인"""
        token = jwt_handler.create_refresh_token(user_id=test_user_data["id"])

        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])

        assert payload["sub"] == str(test_user_data["id"])
        assert payload["type"] == TokenType.REFRESH
        assert "email" not in payload  # Refresh Token에는 email 없음
        assert "iat" in payload
        assert "exp" in payload

    def test_verify_refresh_token_success(self, jwt_handler, test_user_data):
        """Refresh Token 검증 성공"""
        token = jwt_handler.create_refresh_token(user_id=test_user_data["id"])

        payload = jwt_handler.verify_refresh_token(token)

        assert payload["sub"] == str(test_user_data["id"])
        assert payload["type"] == TokenType.REFRESH

    def test_verify_refresh_token_with_access_token_fails(self, jwt_handler, test_user_data):
        """Access Token으로 Refresh Token 검증 시 실패"""
        access_token = jwt_handler.create_access_token(
            user_id=test_user_data["id"],
            email=test_user_data["email"],
        )

        with pytest.raises(ValueError, match="expected refresh token"):
            jwt_handler.verify_refresh_token(access_token)

    # ============== Token Expiry 테스트 ==============

    def test_get_token_expiry_valid_token(self, jwt_handler, test_user_data):
        """유효한 토큰의 만료 시간 조회"""
        token = jwt_handler.create_access_token(
            user_id=test_user_data["id"],
            email=test_user_data["email"],
        )

        expiry = jwt_handler.get_token_expiry(token)

        assert expiry is not None
        assert isinstance(expiry, datetime)
        assert expiry > datetime.now(timezone.utc)

    def test_get_token_expiry_invalid_token(self, jwt_handler):
        """유효하지 않은 토큰의 만료 시간 조회시 None 반환"""
        expiry = jwt_handler.get_token_expiry("invalid.token.here")

        assert expiry is None

    # ============== Decode 테스트 ==============

    def test_decode_token_success(self, jwt_handler, test_user_data):
        """토큰 디코딩 성공"""
        token = jwt_handler.create_access_token(
            user_id=test_user_data["id"],
            email=test_user_data["email"],
        )

        payload = jwt_handler.decode_token(token)

        assert payload["sub"] == str(test_user_data["id"])

    def test_decode_token_wrong_secret_fails(self, jwt_handler, test_user_data):
        """잘못된 secret으로 디코딩 시 실패"""
        from jose import JWTError

        token = jwt_handler.create_access_token(
            user_id=test_user_data["id"],
            email=test_user_data["email"],
        )

        # 다른 secret을 가진 handler로 디코딩 시도
        wrong_handler = JWTHandler(secret_key="wrong_secret")

        with pytest.raises(JWTError):
            wrong_handler.decode_token(token)


class TestTokenType:
    """TokenType 상수 테스트"""

    def test_token_types(self):
        """토큰 타입 상수 확인"""
        assert TokenType.ACCESS == "access"
        assert TokenType.REFRESH == "refresh"
