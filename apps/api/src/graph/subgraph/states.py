from typing_extensions import Annotated
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class QueryState:
    """Private state for the retrieve_documents node in the researcher graph."""
    query: str
    
    
