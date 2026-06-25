from typing import TypedDict


class AgentState(TypedDict):
    """The graph state definition for our Email Classification agent."""

    subject: str
    body: str
    category: str | None
    confidence: float | None
    reason: str | None
