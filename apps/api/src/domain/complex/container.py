"""Complex 도메인 DI 컨테이너"""
from dependency_injector import containers, providers

from .repository import ComplexRepository
from .service import ComplexService


class ComplexContainer(containers.DeclarativeContainer):
    """Complex 도메인 DI 컨테이너"""

    # Repository
    complex_repository = providers.Singleton(ComplexRepository)

    # Service
    complex_service = providers.Singleton(
        ComplexService,
        repository=complex_repository,
    )
