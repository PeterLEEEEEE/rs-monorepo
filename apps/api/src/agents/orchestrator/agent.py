from typing import Any, AsyncIterator, Optional

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from src.agents.base import BaseAgent, AgentConfig, AgentType
from .prompts import ORCHESTRATOR_SYSTEM_PROMPT


class OrchestratorAgent(BaseAgent):
    """오케스트레이터 에이전트 - 사용자 질의를 적절한 에이전트로 라우팅"""

    def __init__(
        self,
        llm: Any,
        session_factory: Any,
        sub_agents: Optional[dict[AgentType, BaseAgent]] = None,
    ):
        config = AgentConfig(
            name="Orchestrator Agent",
            description="사용자 질의를 분석하여 적절한 전문 에이전트로 라우팅하는 오케스트레이터",
        )
        super().__init__(config, llm)
        self.session_factory = session_factory

        # Sub-agents는 외부에서 주입받음
        self.sub_agents = sub_agents or {}

    def get_tools(self) -> list:
        """오케스트레이터의 도구: 다른 에이전트 호출"""

        @tool
        async def call_property_agent(query: str) -> str:
            """매물 검색 및 단지 정보 조회 에이전트 호출

            Args:
                query: 사용자 질의 (예: "헬리오시티 매물 보여줘")

            Returns:
                Property Agent의 응답
            """
            agent = self.sub_agents[AgentType.PROPERTY]
            result = await agent.invoke(query, context_id="orchestrator")
            messages = result.get("messages", [])
            if messages:
                return messages[-1].content
            return "매물 정보를 찾을 수 없습니다."

        @tool
        async def call_market_agent(query: str) -> str:
            """실거래가 및 시세 분석 에이전트 호출

            Args:
                query: 사용자 질의 (예: "헬리오시티 실거래가 알려줘")

            Returns:
                Market Agent의 응답
            """
            agent = self.sub_agents[AgentType.MARKET]
            result = await agent.invoke(query, context_id="orchestrator")
            messages = result.get("messages", [])
            if messages:
                return messages[-1].content
            return "시세 정보를 찾을 수 없습니다."

        @tool
        async def call_comparison_agent(query: str) -> str:
            """단지 비교 분석 에이전트 호출

            Args:
                query: 사용자 질의 (예: "헬리오시티랑 서초힐스 비교해줘")

            Returns:
                Comparison Agent의 응답
            """
            agent = self.sub_agents[AgentType.COMPARISON]
            result = await agent.invoke(query, context_id="orchestrator")
            messages = result.get("messages", [])
            if messages:
                return messages[-1].content
            return "비교 정보를 찾을 수 없습니다."

        return [call_property_agent, call_market_agent, call_comparison_agent]

    def get_system_prompt(self) -> str:
        return ORCHESTRATOR_SYSTEM_PROMPT

    def get_sub_agent(self, agent_type: AgentType) -> BaseAgent:
        """특정 서브 에이전트 반환"""
        return self.sub_agents.get(agent_type)

    def list_sub_agents(self) -> list[dict]:
        """모든 서브 에이전트 정보 반환"""
        return [
            {
                "type": agent_type.value,
                "name": agent.config.name,
                "description": agent.config.description,
            }
            for agent_type, agent in self.sub_agents.items()
        ]
