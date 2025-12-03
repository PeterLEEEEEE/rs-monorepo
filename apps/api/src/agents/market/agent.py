from typing import Any

from src.agents.base import BaseAgent, AgentConfig
from .tools import MarketTools
from .prompts import MARKET_AGENT_SYSTEM_PROMPT


class MarketAgent(BaseAgent):
    """부동산 시세 및 실거래가 분석 에이전트"""

    def __init__(self, llm: Any, session_factory: Any):
        config = AgentConfig(
            name="Market Agent",
            description="부동산 실거래가 조회 및 시세 분석 전문 에이전트",
        )
        super().__init__(config, llm)
        self.tools_provider = MarketTools(session_factory)

    def get_tools(self) -> list:
        return self.tools_provider.get_tools()

    def get_system_prompt(self) -> str:
        return MARKET_AGENT_SYSTEM_PROMPT
