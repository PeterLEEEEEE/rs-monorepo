from dependency_injector import containers, providers

from src.agents import OrchestratorAgent
from .service import ChatService
from .repository import ChatRepository


class ChatContainer(containers.DeclarativeContainer):
    """Container for chat domain dependencies."""

    # Orchestrator는 AgentContainer에서 주입받음 (Singleton)
    orchestrator = providers.Dependency(instance_of=OrchestratorAgent)

    chat_repository = providers.Factory(ChatRepository)

    chat_service = providers.Factory(
        ChatService,
        repository=chat_repository,
        orchestrator=orchestrator,
    )