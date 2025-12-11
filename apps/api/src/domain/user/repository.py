from typing import List, Optional
from sqlalchemy import select, delete

from src.db.session import session
from .models import User


class UserRepository:
    """User Repository - 글로벌 scoped session 사용"""

    async def get_all(self) -> List[User]:
        query = select(User)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        query = delete(User).where(User.id == user_id)
        result = await session.execute(query)
        await session.flush()
        return result.rowcount > 0
