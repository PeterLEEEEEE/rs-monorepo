"""Market 도메인 DI 컨테이너"""
from dependency_injector import containers, providers

from .repository import MarketRepository
from .service import MarketService


class MarketContainer(containers.DeclarativeContainer):
    """Market 도메인 DI 컨테이너"""

    market_repository = providers.Singleton(MarketRepository)

    market_service = providers.Singleton(
        MarketService,
        repository=market_repository,
    )
