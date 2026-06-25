from typing import TypedDict


class AgentState(TypedDict):
    """The graph state definition for our Email Classification agent."""

    subject: str
    body: str
    category: str | None
    reason: str | None
    JudgeVerted: str | None
    JudgeReasoning: str | None

