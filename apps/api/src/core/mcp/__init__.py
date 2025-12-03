from __future__ import annotations

from fastmcp import FastMCP
from pydantic import BaseModel, Field


class PingInput(BaseModel):
    """Input payload for the ping tool."""

    message: str = Field(
        default="pong",
        description="Text to echo back in the response",
    )


class PingOutput(BaseModel):
    """Structured response for the ping tool."""

    reply: str = Field(description="The echoed message")


def register_basic_tools(mcp: FastMCP) -> None:
    """Attach basic test tools to the MCP instance."""

    @mcp.tool(name="ping", description="Echo back a message to test MCP wiring")
    async def ping(payload: PingInput) -> PingOutput:  # noqa: WPS430 (nested function)
        return PingOutput(reply=payload.message)
