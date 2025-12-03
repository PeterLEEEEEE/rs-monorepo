"""Langfuse integration for LLM observability."""

from typing import Optional

from langfuse import Langfuse
from langfuse.callback import CallbackHandler


_langfuse_initialized = False


def _ensure_langfuse_client():
    """Initialize Langfuse client singleton if not already done."""
    global _langfuse_initialized
    if _langfuse_initialized:
        return

    from src.core.config import get_config
    config = get_config()

    pk = getattr(config, 'LANGFUSE_PUBLIC_KEY', None)
    sk = getattr(config, 'LANGFUSE_SECRET_KEY', None)
    host = getattr(config, 'LANGFUSE_HOST', None)

    if pk and sk:
        Langfuse(
            public_key=pk,
            secret_key=sk,
            host=host,
        )
        _langfuse_initialized = True


def get_langfuse_handler(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    trace_name: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> Optional[CallbackHandler]:
    """
    Create a Langfuse callback handler for LangChain/LangGraph.

    Args:
        user_id: Optional user identifier for tracking
        session_id: Optional session/conversation identifier
        trace_name: Optional name for the trace
        tags: Optional list of tags

    Returns:
        CallbackHandler instance or None if Langfuse is not configured
    """
    from src.core.config import get_config
    config = get_config()

    pk = getattr(config, 'LANGFUSE_PUBLIC_KEY', None)
    sk = getattr(config, 'LANGFUSE_SECRET_KEY', None)

    if not pk or not sk:
        return None

    # Ensure client is initialized
    _ensure_langfuse_client()

    return CallbackHandler(
        user_id=user_id,
        session_id=session_id,
        trace_name=trace_name,
        tags=tags,
    )


def create_trace_handler(
    context_id: str,
    agent_name: str,
    user_id: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> Optional[CallbackHandler]:
    """
    Create a trace handler with agent context.

    This is a convenience function that sets up common trace parameters
    for agent invocations.

    Args:
        context_id: The conversation/thread context ID
        agent_name: Name of the agent being invoked
        user_id: Optional user identifier
        tags: Optional additional tags

    Returns:
        CallbackHandler instance or None if Langfuse is not configured
    """
    trace_tags = [agent_name] + (tags or [])

    return get_langfuse_handler(
        user_id=user_id,
        session_id=context_id,
        trace_name=f"{agent_name}:invoke",
        tags=trace_tags,
    )
