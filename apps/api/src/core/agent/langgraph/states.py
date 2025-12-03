from dataclass import dataclass

from langgraph.graph import add_messages

from typing_extensions import TypedDict, Annotated, Literal


@dataclass(kw_only=True) 
class InputState:
    messages: Annotated[list, add_messages]


@dataclass(kw_only=True)
class SummaryState(InputState):
    summary: str
