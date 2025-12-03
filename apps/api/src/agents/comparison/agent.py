from typing import Any

from src.agents.base import BaseAgent, AgentConfig
from .tools import ComparisonTools
from .prompts import COMPARISON_AGENT_SYSTEM_PROMPT


class ComparisonAgent(BaseAgent):
    """부동산 비교 분석 에이전트"""

    def __init__(self, llm: Any, session_factory: Any):
        config = AgentConfig(
            name="Comparison Agent",
            description="아파트 단지 간 비교 분석 전문 에이전트",
        )
        super().__init__(config, llm)
        self.tools_provider = ComparisonTools(session_factory)

    def get_tools(self) -> list:
        return self.tools_provider.get_tools()

    def get_system_prompt(self) -> str:
        return COMPARISON_AGENT_SYSTEM_PROMPT
