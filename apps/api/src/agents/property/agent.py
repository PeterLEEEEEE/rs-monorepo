from typing import Any

from src.agents.base import BaseAgent, AgentConfig
from .tools import PropertyTools
from .prompts import PROPERTY_AGENT_SYSTEM_PROMPT


class PropertyAgent(BaseAgent):
    """부동산 매물 검색 에이전트"""

    def __init__(self, llm: Any, session_factory: Any):
        config = AgentConfig(
            name="Property Agent",
            description="부동산 매물 검색 및 단지 정보 조회 전문 에이전트",
        )
        super().__init__(config, llm)
        self.tools_provider = PropertyTools(session_factory)

    def get_tools(self) -> list:
        return self.tools_provider.get_tools()

    def get_system_prompt(self) -> str:
        return PROPERTY_AGENT_SYSTEM_PROMPT
