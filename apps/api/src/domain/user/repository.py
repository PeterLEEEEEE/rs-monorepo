from typing import List, Optional, Type
from sqlalchemy import select, delete

from .models import User
from .base import BaseAlchemyRepository


class UserRepository(BaseAlchemyRepository[User]):
    
    def __init__(self, session_factory):
        super().__init__(model=User, session_factory=session_factory)
    
    async def get_all(self) -> List[User]:
        async with self.session_factory() as session:
            query = select(User)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        async with self.session_factory() as session:
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        async with self.session_factory() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self.session_factory() as session:
            query = select(User).where(User.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        async with self.session_factory() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def update(self, user: User) -> User:
        async with self.session_factory() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def delete(self, user_id: int) -> bool:
        async with self.session_factory() as session:
            query = delete(User).where(User.id == user_id)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0


