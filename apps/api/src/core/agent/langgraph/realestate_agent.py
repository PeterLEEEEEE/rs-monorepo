from typing import Annotated, Sequence, TypedDict  # Sequence는 문자열(str), 리스트(list), 튜플(tuple) 전부 받을 수 있음
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from src.core.agent.llm import get_llm
from .tools import get_complex_infos, get_complex_overview, get_complex_id


class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a, b):
    """add a, b

    Args:
        a (_type_): _description_
        b (_type_): _description_

    Returns:
        _type_: _description_
    """
    return a + b
# tools = [
#     get_complex_infos,
#     get_complex_overview,
#     get_complex_id
# ]

tools = [add]

def should_continue(state: AgentState):
    messages = state.messages
    last_message = messages[-1] if messages else None
    if not last_message.tool_calls: # tool 필요 없으면 끝
        return "end"
    else:
        return "continue"
    
def llm_call(state: AgentState) -> AgentState:
    """This will be called by the agent to process the state.
    
    Args:
        state (AgentState): _description_

    Returns:
        AgentState: _description_
    """
    system_prompt = SystemMessage(
        content="You are a real estate agent. You can answer questions about real estate properties."
    )
    
    llm = get_llm().bind_tools(tools)
    response = llm.invoke([system_prompt] + state.messages)
    # state.messages = AIMessage(content=response.content)
    
    # return state
    return {"messages": [response]}


graph = StateGraph(AgentState)
graph.add_node("agent", llm_call)
graph.set_entry_point("agent")

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)
graph.add_conditional_edges(
    "agent",
    path=should_continue,
    path_map={
        "continue": "tools", 
        "end": END
    }
)

graph.add_edge("tools", "agent")

agent = graph.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", "Add 3 + 4")]}
print_stream(agent.stream(inputs, stream_mode="values"))