"""Auth 도메인 Repository"""
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, delete

from src.db.base_repository import BaseRepository
from .models import RefreshToken


class RefreshTokenRepository(BaseRepository):
    """Refresh Token Repository"""

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Refresh Token 저장"""
        self.session.add(refresh_token)
        await self.session.flush()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """토큰 값으로 조회"""
        query = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> List[RefreshToken]:
        """사용자의 모든 Refresh Token 조회"""
        query = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_by_token(self, token: str) -> bool:
        """토큰 삭제"""
        query = delete(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def delete_by_user_id(self, user_id: int) -> int:
        """사용자의 모든 Refresh Token 삭제 (강제 로그아웃)"""
        query = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def delete_expired(self) -> int:
        """만료된 토큰 정리"""
        query = delete(RefreshToken).where(RefreshToken.expires_at < datetime.now(timezone.utc))
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def delete_by_user_and_device(self, user_id: int, device_id: str) -> int:
        """같은 사용자 + 같은 디바이스의 기존 토큰 삭제"""
        query = delete(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.device_info == device_id
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount
