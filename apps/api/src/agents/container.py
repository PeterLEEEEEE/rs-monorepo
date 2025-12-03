"""Agent Dependency Injection Container."""

from dependency_injector import containers, providers

from src.agents.base import AgentType
from src.agents.property.agent import PropertyAgent
from src.agents.market.agent import MarketAgent
from src.agents.comparison.agent import ComparisonAgent
from src.agents.orchestrator.agent import OrchestratorAgent


class AgentContainer(containers.DeclarativeContainer):
    """Container for agent dependencies with singleton management."""

    # Dependencies from parent container
    llm = providers.Dependency()
    session_factory = providers.Dependency()

    # Sub-agents as singletons
    property_agent = providers.Singleton(
        PropertyAgent,
        llm=llm,
        session_factory=session_factory,
    )

    market_agent = providers.Singleton(
        MarketAgent,
        llm=llm,
        session_factory=session_factory,
    )

    comparison_agent = providers.Singleton(
        ComparisonAgent,
        llm=llm,
        session_factory=session_factory,
    )

    # Sub-agents dict for orchestrator
    sub_agents = providers.Dict({
        AgentType.PROPERTY: property_agent,
        AgentType.MARKET: market_agent,
        AgentType.COMPARISON: comparison_agent,
    })

    # Orchestrator with injected sub-agents
    orchestrator = providers.Singleton(
        OrchestratorAgent,
        llm=llm,
        session_factory=session_factory,
        sub_agents=sub_agents,
    )
