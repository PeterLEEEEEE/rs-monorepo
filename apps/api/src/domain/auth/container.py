from dependency_injector import containers, providers

from src.domain.user.repository import UserRepository
from .repository import RefreshTokenRepository
from .service import AuthService


class AuthContainer(containers.DeclarativeContainer):
    """Auth 도메인 DI 컨테이너"""

    # 외부에서 주입받을 의존성
    redis_client = providers.Dependency()

    # Repository (글로벌 session 사용, 주입 불필요)
    user_repository = providers.Singleton(UserRepository)
    refresh_token_repository = providers.Singleton(RefreshTokenRepository)

    # Service
    auth_service = providers.Singleton(
        AuthService,
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
        redis_client=redis_client,
    )
