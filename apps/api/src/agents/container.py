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

    # Sub-agents as singletons (글로벌 session 사용, 주입 불필요)
    property_agent = providers.Singleton(PropertyAgent, llm=llm)
    market_agent = providers.Singleton(MarketAgent, llm=llm)
    comparison_agent = providers.Singleton(ComparisonAgent, llm=llm)

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
        sub_agents=sub_agents,
    )
