from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.pregel import Pregel
from .prompts.system_template import SYSTEM_INSTRUCTION
from .tools.api_tools import (
    get_complex_infos,
    get_complex_overview,
    get_complex_id
)


class RealEstateAgent:
    def __init__(self, llm: AzureChatOpenAI, checkpointer=None):
        self.llm = llm
        self.tools = [get_complex_infos, get_complex_overview] # get_complex_id
        self.checkpointer = checkpointer
        # Graph를 미리 생성하지 않고 필요할 때 생성
        self._graph = None

    def get_graph(self) -> Pregel:
        if self._graph is None:
            self._graph = create_react_agent(
                self.llm,
                tools=self.tools,
                checkpointer=self.checkpointer,
                prompt=SYSTEM_INSTRUCTION
            )
        return self._graph
        # self.graph = create_react_agent(
        #     self.llm,
        #     tools=self.tools,
        #     checkpointer=self.checkpointer,
        #     prompt=SYSTEM_INSTRUCTION
        # )

    def invoke(self, query, context_id):
        ...
    
    async def stream(self, query, context_id):
        """
        Stream the response from the agent.
        """
        memory_config = {"configurable": {"thread_id": context_id}}
        async for response in self.graph.astream(query, config=memory_config, stream_mode="updates"):
            yield response
    