from dataclass import dataclass

from langgraph.graph import add_messages

from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated, Literal


@dataclass(kw_only=True) # 키워드 인자로만 전달하는 옵션
class InputState:
    messages: Annotated[list, add_messages]

class Router(TypedDict):
    """
    Classify the user's query
    """
    
    logic: str
    type: Literal[""]

@dataclass(kw_only=True)
class AgentState(InputState):
    pass


class State(TypedDict):
    messages: Annotated[list, add_messages]


@dataclass(kw_only=True)
class SummaryState(State):
    summary: str