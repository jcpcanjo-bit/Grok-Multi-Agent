from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Gemeinsamer Zustand. `messages` wird angehängt, der Rest überschrieben."""

    question: str
    plan: str
    messages: Annotated[list[AnyMessage], add_messages]
    notes: str
    answer: str
    tool_rounds: int
