from typing import Optional
from datetime import datetime, timedelta, timezone
from logger import logger
from redis.asyncio import Redis

from src.core.security.jwt import jwt_handler
from src.core.config.settings import config
from src.db.transactional import transactional
from src.domain.user.repository import UserRepository
from src.domain.user.service import check_password
from src.domain.user.models import User

from .dtos import LoginResult, UserResponse, RefreshResponse
from .models import RefreshToken
from .repository import RefreshTokenRepository


# Redis 블랙리스트 키 prefix
BLACKLIST_PREFIX = "token_blacklist:"


class AuthService:
    """인증 서비스"""

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        redis_client: Redis,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.redis_client = redis_client

    @transactional
    async def login(self, email: str, password: str, device_id: str | None = None, ip_address: str | None = None) -> Optional[LoginResult]:
        """
        로그인 처리

        Args:
            email: 사용자 이메일
            password: 비밀번호

        Returns:
            LoginResponse or None (인증 실패 시)
        """
        # 1. 사용자 조회
        user = await self.user_repository.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: user not found - {email}")
            return None

        # 2. 비밀번호 검증
        if not check_password(user.hashed_password, password):
            logger.warning(f"Login failed: invalid password - {email}")
            return None

        # 3. 계정 활성화 확인
        if not user.is_active:
            logger.warning(f"Login failed: inactive account - {email}")
            return None

        # 4. 같은 디바이스의 기존 토큰 삭제 (디바이스당 하나의 세션만 유지)
        if device_id:
            deleted = await self.refresh_token_repository.delete_by_user_and_device(user.id, device_id)
            if deleted > 0:
                logger.info(f"Deleted {deleted} existing token(s) for device: {device_id}")

        # 5. 토큰 생성
        access_token = jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        refresh_token = jwt_handler.create_refresh_token(user_id=user.id)

        # 6. Refresh Token DB 저장
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_entity = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            created_at=now,
            device_info=device_id,
            ip_address=ip_address,
        )
        await self.refresh_token_repository.create(refresh_token_entity)

        logger.info(f"Login successful: {email}")

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role,
            ),
        )

    @transactional
    async def refresh_access_token(self, refresh_token: str) -> Optional[RefreshResponse]:
        """
        Access Token 갱신

        Args:
            refresh_token: Refresh Token

        Returns:
            RefreshResponse or None (토큰 유효하지 않을 시)
        """
        try:
            # 1. Refresh Token JWT 서명 검증
            payload = jwt_handler.verify_refresh_token(refresh_token)
            user_id = int(payload.get("sub"))

            # 2. DB에서 Refresh Token 존재 여부 확인
            stored_token = await self.refresh_token_repository.get_by_token(refresh_token)
            if not stored_token:
                logger.warning(f"Token refresh failed: token not found in DB - user_id={user_id}")
                return None

            # 3. 토큰 만료 확인
            if stored_token.expires_at < datetime.now(timezone.utc):
                logger.warning(f"Token refresh failed: token expired - user_id={user_id}")
                await self.refresh_token_repository.delete_by_token(refresh_token)
                return None

            # 4. 사용자 조회 (여전히 유효한 사용자인지 확인)
            user = await self.user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                logger.warning(f"Token refresh failed: user not found or inactive - {user_id}")
                return None

            # 5. 새 Access Token 생성
            access_token = jwt_handler.create_access_token(
                user_id=user.id,
                email=user.email,
                role=user.role,
            )

            logger.info(f"Token refreshed: user_id={user_id}")

            return RefreshResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        except Exception as e:
            logger.warning(f"Token refresh failed: {e}")
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """사용자 ID로 조회"""
        return await self.user_repository.get_by_id(user_id)

    async def add_token_to_blacklist(self, token: str) -> bool:
        """
        Access Token을 블랙리스트에 추가 (로그아웃 시 사용)

        Args:
            token: 블랙리스트에 추가할 JWT Access Token

        Returns:
            성공 여부
        """
        try:
            # 토큰의 남은 유효기간 계산
            expiry = jwt_handler.get_token_expiry(token)
            if not expiry:
                # 토큰이 이미 만료되었거나 유효하지 않으면 블랙리스트 추가 불필요
                return True

            now = datetime.now(timezone.utc)
            ttl_seconds = int((expiry - now).total_seconds())

            if ttl_seconds <= 0:
                # 이미 만료된 토큰
                return True

            # Redis에 토큰 추가 (토큰 만료 시간까지만 유지)
            key = f"{BLACKLIST_PREFIX}{token}"
            await self.redis_client.setex(key, ttl_seconds, "blacklisted")
            logger.info(f"Access token added to blacklist, TTL: {ttl_seconds}s")
            return True

        except Exception as e:
            logger.error(f"Failed to add token to blacklist: {e}")
            return False

    @transactional
    async def logout(self, access_token: str, refresh_token: str) -> bool:
        """
        로그아웃 처리

        - Access Token을 Redis 블랙리스트에 추가
        - Refresh Token을 DB에서 삭제

        Args:
            access_token: Access Token
            refresh_token: Refresh Token

        Returns:
            성공 여부
        """
        try:
            # 1. Access Token 블랙리스트 추가
            await self.add_token_to_blacklist(access_token)

            # 2. Refresh Token DB에서 삭제
            await self.refresh_token_repository.delete_by_token(refresh_token)

            logger.info("Logout successful")
            return True

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False

    @transactional
    async def logout_all_devices(self, user_id: int) -> int:
        """
        모든 기기에서 로그아웃 (강제 로그아웃)

        Args:
            user_id: 사용자 ID

        Returns:
            삭제된 토큰 수
        """
        try:
            deleted_count = await self.refresh_token_repository.delete_by_user_id(user_id)
            logger.info(f"Logged out from all devices: user_id={user_id}, deleted={deleted_count}")
            return deleted_count
        except Exception as e:
            logger.error(f"Logout all devices failed: {e}")
            return 0

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        토큰이 블랙리스트에 있는지 확인

        Args:
            token: 확인할 JWT 토큰

        Returns:
            블랙리스트에 있으면 True
        """
        try:
            key = f"{BLACKLIST_PREFIX}{token}"
            result = await self.redis_client.get(key)
            return result is not None
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False
