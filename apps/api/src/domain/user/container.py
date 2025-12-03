from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from redis.asyncio.client import Redis
from .repository import UserRepository
from .service import UserService
from .models import User


class UserContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency()
    
    # 레포지토리에 세션 주입
    user_repository = providers.Factory(
        UserRepository,
        session_factory=session_factory
    )
    
    # 서비스에 레포지토리 주입
    user_service = providers.Factory(
        UserService, 
        repository=user_repository,
    )
