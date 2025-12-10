"""Auth 도메인 Repository"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, delete

from .models import RefreshToken


class RefreshTokenRepository:
    """Refresh Token Repository"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Refresh Token 저장"""
        async with self.session_factory() as session:
            session.add(refresh_token)
            await session.commit()
            await session.refresh(refresh_token)
            return refresh_token

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """토큰 값으로 조회"""
        async with self.session_factory() as session:
            query = select(RefreshToken).where(RefreshToken.token == token)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> List[RefreshToken]:
        """사용자의 모든 Refresh Token 조회"""
        async with self.session_factory() as session:
            query = select(RefreshToken).where(RefreshToken.user_id == user_id)
            result = await session.execute(query)
            return list(result.scalars().all())

    async def delete_by_token(self, token: str) -> bool:
        """토큰 삭제"""
        async with self.session_factory() as session:
            query = delete(RefreshToken).where(RefreshToken.token == token)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0

    async def delete_by_user_id(self, user_id: int) -> int:
        """사용자의 모든 Refresh Token 삭제 (강제 로그아웃)"""
        async with self.session_factory() as session:
            query = delete(RefreshToken).where(RefreshToken.user_id == user_id)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount

    async def delete_expired(self) -> int:
        """만료된 토큰 정리"""
        async with self.session_factory() as session:
            query = delete(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
            result = await session.execute(query)
            await session.commit()
            return result.rowcount

    async def delete_by_user_and_device(self, user_id: int, device_id: str) -> int:
        """같은 사용자 + 같은 디바이스의 기존 토큰 삭제"""
        async with self.session_factory() as session:
            query = delete(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.device_info == device_id
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount
