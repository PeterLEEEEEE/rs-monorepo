from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional
from dataclasses import dataclass
from enum import Enum

from a2a.types import AgentCard, AgentCapabilities, AgentSkill


class AgentType(str, Enum):
    """Agent types for routing."""
    PROPERTY = "property"
    MARKET = "market"
    COMPARISON = "comparison"


@dataclass
class AgentConfig:
    name: str
    description: str
    version: str = "1.0.0"


class BaseAgent(ABC):
    """Base class for all A2A agents."""

    def __init__(self, config: AgentConfig, llm: Any):
        self.config = config
        self.llm = llm
        self._graph = None

    @abstractmethod
    def get_tools(self) -> list:
        """Return list of tools available to this agent."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    def get_graph(self):
        """Lazy initialization of the agent graph."""
        if self._graph is None:
            from langgraph.prebuilt import create_react_agent
            self._graph = create_react_agent(
                self.llm,
                tools=self.get_tools(),
                prompt=self.get_system_prompt(),
            )
        return self._graph

    def _get_langfuse_callback(
        self,
        context_id: str,
        user_id: Optional[str] = None,
    ):
        """Get Langfuse callback handler if configured."""
        try:
            from src.core.observability import create_trace_handler
            return create_trace_handler(
                context_id=context_id,
                agent_name=self.config.name,
                user_id=user_id,
            )
        except Exception:
            return None

    async def invoke(
        self,
        query: str,
        context_id: str,
        user_id: Optional[str] = None,
    ) -> dict:
        """Invoke the agent with a query.

        Args:
            query: User query string
            context_id: Conversation/thread context ID
            user_id: Optional user identifier for tracing
        """
        return await self.invoke_with_history(
            messages=[("user", query)],
            context_id=context_id,
            user_id=user_id,
        )

    async def invoke_with_history(
        self,
        messages: list[tuple[str, str]],
        context_id: str,
        user_id: Optional[str] = None,
    ) -> dict:
        """Invoke the agent with message history.

        Args:
            messages: List of (role, content) tuples
            context_id: Conversation/thread context ID
            user_id: Optional user identifier for tracing
        """
        graph = self.get_graph()

        config = {"configurable": {"thread_id": context_id}}

        # Add Langfuse callback if available
        callback = self._get_langfuse_callback(context_id, user_id)
        if callback:
            config["callbacks"] = [callback]

        result = await graph.ainvoke({"messages": messages}, config=config)
        return result

    async def stream(
        self,
        query: str,
        context_id: str,
        user_id: Optional[str] = None,
    ) -> AsyncIterator[dict]:
        """Stream responses from the agent.

        Args:
            query: User query string
            context_id: Conversation/thread context ID
            user_id: Optional user identifier for tracing
        """
        graph = self.get_graph()

        config = {"configurable": {"thread_id": context_id}}

        # Add Langfuse callback if available
        callback = self._get_langfuse_callback(context_id, user_id)
        if callback:
            config["callbacks"] = [callback]

        async for chunk in graph.astream(
            {"messages": [("user", query)]},
            config=config,
            stream_mode="updates"
        ):
            yield chunk

    def get_agent_card(self) -> AgentCard:
        """Return A2A agent card for discovery."""
        return AgentCard(
            name=self.config.name,
            description=self.config.description,
            version=self.config.version,
            capabilities=AgentCapabilities(streaming=True),
            skills=[
                AgentSkill(
                    id=self.config.name.lower().replace(" ", "_"),
                    name=self.config.name,
                    description=self.config.description,
                )
            ],
        )
