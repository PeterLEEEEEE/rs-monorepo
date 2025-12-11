"""Real Price 도메인 DI 컨테이너"""
from dependency_injector import containers, providers

from .repository import RealPriceRepository
from .service import RealPriceService


class RealPriceContainer(containers.DeclarativeContainer):
    """Real Price 도메인 DI 컨테이너"""

    # Repository (글로벌 session 사용, 주입 불필요)
    real_price_repository = providers.Singleton(RealPriceRepository)

    # Service
    real_price_service = providers.Singleton(
        RealPriceService,
        repository=real_price_repository,
    )
