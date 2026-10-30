from langchain_core.messages import HumanMessage, SystemMessage

from grok_agents.llm import make_llm
from grok_agents.state import AgentState
from grok_agents.tools import MAX_TOOL_ROUNDS, web_search


def _text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
        return "\n".join(parts)
    return str(content)


def planner(state: AgentState) -> dict:
    """Zerlegt die Frage in konkrete Suchaufträge. Ruft kein Tool auf."""
    response = make_llm().invoke(
        [
            SystemMessage(
                content=(
                    "Du bist der Planner. Zerlege die Frage in 2 bis 4 "
                    "konkrete Suchaufträge. Antworte nur mit einer kurzen "
                    "nummerierten Liste. Beantworte die Frage nicht."
                )
            ),
            HumanMessage(content=state["question"]),
        ]
    )
    return {"plan": _text(response.content)}


def researcher(state: AgentState) -> dict:
    """Sucht mit web_search und schreibt danach Notizen mit URLs."""
    history = list(state["messages"])
    new_messages = []

    if not history:
        new_messages = [
            SystemMessage(
                content=(
                    "Du bist der Researcher. Du hast das Tool web_search. "
                    "Suche zuerst, ein bis drei kurze Queries reichen. "
                    "Wenn die Treffer reichen, schreibe knappe Notizen auf "
                    "Deutsch und nenne die URLs. Erfinde keine Fakten und keine Links."
                )
            ),
            HumanMessage(
                content=f"Frage: {state['question']}\n\nPlan:\n{state['plan']}"
            ),
        ]
        history = list(new_messages)
    elif state["tool_rounds"] >= MAX_TOOL_ROUNDS:
        stop = HumanMessage(
            content=(
                "Keine weitere Suche. Schreibe jetzt die Notizen aus den "
                "bisherigen Treffern. Rufe kein Tool auf."
            )
        )
        new_messages.append(stop)
        history = history + [stop]

    llm = make_llm()
    if state["tool_rounds"] < MAX_TOOL_ROUNDS:
        # Erste Runde muss suchen, danach entscheidet das Modell selbst.
        tool_choice = "required" if state["tool_rounds"] == 0 else "auto"
        llm = llm.bind_tools([web_search], tool_choice=tool_choice)

    response = llm.invoke(history)
    # xAI lehnt Assistant-Nachrichten ohne Content ab, auch bei Tool-Calls.
    if getattr(response, "tool_calls", None) and not _text(response.content).strip():
        response.content = "Suche läuft."
    new_messages.append(response)

    notes = state["notes"]
    if not getattr(response, "tool_calls", None):
        notes = _text(response.content)
    return {"messages": new_messages, "notes": notes}


def synthesizer(state: AgentState) -> dict:
    """Schreibt die Antwort aus Plan und Recherche-Notizen."""
    response = make_llm().invoke(
        [
            SystemMessage(
                content=(
                    "Du bist der Synthesizer. Schreibe aus Plan und Notizen "
                    "eine kurze Antwort auf Deutsch. Nenne die Quellen als URLs. "
                    "Wenn etwas in den Notizen fehlt, sag das offen."
                )
            ),
            HumanMessage(
                content=(
                    f"Frage: {state['question']}\n\n"
                    f"Plan:\n{state['plan']}\n\n"
                    f"Notizen:\n{state['notes'] or '(keine)'}"
                )
            ),
        ]
    )
    return {"answer": _text(response.content)}
