from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt, JWTError, ExpiredSignatureError

from src.core.config.settings import config


class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"


class JWTHandler:
    """JWT 토큰 생성 및 검증 핸들러"""

    def __init__(
        self,
        secret_key: str = config.JWT_SECRET,
        algorithm: str = config.JWT_ALGORITHM,
        access_token_expire_minutes: int = config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = config.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self,
        user_id: int,
        email: str,
        role: str = "USER",
        additional_claims: Optional[dict] = None,
    ) -> str:
        """Access Token 생성"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": TokenType.ACCESS,
            "iat": now,
            "exp": expire,
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self,
        user_id: int,
        additional_claims: Optional[dict] = None,
    ) -> str:
        """Refresh Token 생성"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": str(user_id),
            "type": TokenType.REFRESH,
            "iat": now,
            "exp": expire,
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        """
        토큰 디코딩 및 검증

        Raises:
            ExpiredSignatureError: 토큰 만료
            JWTError: 유효하지 않은 토큰
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

    def verify_access_token(self, token: str) -> dict[str, Any]:
        """
        Access Token 검증

        Returns:
            payload dict (sub, email, role, type, iat, exp)

        Raises:
            ValueError: 토큰 타입이 access가 아님
            ExpiredSignatureError: 토큰 만료
            JWTError: 유효하지 않은 토큰
        """
        payload = self.decode_token(token)

        if payload.get("type") != TokenType.ACCESS:
            raise ValueError("Invalid token type: expected access token")

        return payload

    def verify_refresh_token(self, token: str) -> dict[str, Any]:
        """
        Refresh Token 검증

        Returns:
            payload dict (sub, type, iat, exp)

        Raises:
            ValueError: 토큰 타입이 refresh가 아님
            ExpiredSignatureError: 토큰 만료
            JWTError: 유효하지 않은 토큰
        """
        payload = self.decode_token(token)

        if payload.get("type") != TokenType.REFRESH:
            raise ValueError("Invalid token type: expected refresh token")

        return payload

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """토큰 만료 시간 조회"""
        try:
            payload = self.decode_token(token)
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp, tz=timezone.utc)
            return None
        except JWTError:
            return None


# 싱글톤 인스턴스
jwt_handler = JWTHandler()
