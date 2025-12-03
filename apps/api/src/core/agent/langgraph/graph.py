from typing_extensions import Annotated, TypedDict
from dataclasses import dataclass

from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

@dataclass(kw_only=True)
class SummaryState(ChatState):
    summary: str


class RealestateAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def respond(self, state: ChatState) -> dict:
        # Placeholder for agent's response logic
        return {"messages": [f"{self.name} responds to the query."]}


def init_graph():
    agent = RealestateAgent(llm=None)  # Replace with actual LLM instance
    tool_node = ToolNode(tools=[])
    graph_builder = StateGraph(ChatState)
    graph_builder.add_node("realestate_agent", agent)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges(
            "realestate_agent",
            # path=route_tools,
            # path_map={"tools": "tools", END: END},
            tools_condition
        )

    graph_builder.add_edge(START, "realestate_agent")
    graph_builder.add_edge("tools", "realestate_agent")
    
    return graph_builder.compile()


graph = init_graph()