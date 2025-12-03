import bcrypt

from typing import List, Optional, Dict, Any
from dependency_injector.wiring import Provide, inject

from src.core.handler.exception import AlreadyExistUserEx
from .repository import UserRepository
from .models import User
from .base import BaseService
from .dtos import CreateUserRequest, CreateUserResponse


def hash_password(password: str) -> str:
    byte_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(byte_password, salt)
    return hashed_password.decode("utf-8")


def check_password(hashed_password: str, user_password: str) -> bool:
    byte_password = user_password.encode("utf-8")
    return bcrypt.checkpw(byte_password, hashed_password.encode("utf-8"))


class UserService(BaseService):
    
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
    
    async def get_all_users(self) -> List[User]:
        return await self.repository.get_all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email)

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        # 비밀번호 해싱 로직은 실제 구현에서 추가할 수 있습니다
        
        hashed_password = hash_password(user_data['password'])
        user_exists = await self.repository.get_by_email(user_data['email'])
        
        if user_exists:
            raise AlreadyExistUserEx
        
        user = await self.repository.create(User(
            username=user_data['username'],
            email=user_data['email'],
            hashed_password=hashed_password, 
        ))
        
        return CreateUserResponse(id=user.id, email=user.email)

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        user = await self.repository.get_by_id(user_id)
        if not user:
            return None
            
        # 업데이트할 필드 설정
        for key, value in user_data.items():
            if hasattr(user, key) and key != 'id':
                setattr(user, key, value)
                
        return await self.repository.update(user)

    async def delete_user(self, user_id: int) -> bool:
        return await self.repository.delete(user_id)