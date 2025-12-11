from typing import List, Optional
from sqlalchemy import select, delete

from src.db.base_repository import BaseRepository
from .models import User


class UserRepository(BaseRepository):
    """User Repository"""

    async def get_all(self) -> List[User]:
        query = select(User)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        query = delete(User).where(User.id == user_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0
