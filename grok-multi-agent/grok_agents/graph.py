from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from grok_agents.agents import planner, researcher, synthesizer
from grok_agents.state import AgentState
from grok_agents.tools import web_search

# ToolNode führt die tool_calls der letzten AIMessage aus und hängt ToolMessages an.
_tool_node = ToolNode([web_search])


def run_tools(state: AgentState) -> dict:
    update = _tool_node.invoke(state)
    update["tool_rounds"] = state["tool_rounds"] + 1
    return update


def route_after_researcher(state: AgentState) -> Literal["tools", "synthesizer"]:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return "synthesizer"


def build_graph():
    """Planner -> Researcher <-> Tools -> Synthesizer.

    Der Researcher bekommt web_search über bind_tools. Liegt ein tool_call
    in der Antwort, geht die Kante an run_tools und danach zurück.
    """
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner)
    graph.add_node("researcher", researcher)
    graph.add_node("tools", run_tools)
    graph.add_node("synthesizer", synthesizer)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_conditional_edges(
        "researcher",
        route_after_researcher,
        {"tools": "tools", "synthesizer": "synthesizer"},
    )
    graph.add_edge("tools", "researcher")
    graph.add_edge("synthesizer", END)
    return graph.compile()
