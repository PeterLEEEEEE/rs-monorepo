from dependency_injector import containers, providers

from .repository import UserRepository
from .service import UserService


class UserContainer(containers.DeclarativeContainer):
    # Repository (글로벌 session 사용, 주입 불필요)
    user_repository = providers.Factory(UserRepository)

    # Service
    user_service = providers.Factory(
        UserService,
        repository=user_repository,
    )
