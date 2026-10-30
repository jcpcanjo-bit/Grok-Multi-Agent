# Grok-Multi-Agent# Grok Multi-Agent (LangGraph)

Drei Agenten beantworten eine Frage. Der Researcher sucht vorher im Web.

```text
START → planner → researcher ⇄ tools → synthesizer → END
```

| Agent | Aufgabe |
| --- | --- |
| Planner | Macht aus der Frage 2–4 Suchaufträge. |
| Researcher | Ruft `web_search` (DuckDuckGo) auf und schreibt Notizen mit URLs. |
| Synthesizer | Formuliert die Antwort aus Plan und Notizen. |

Modell ist `grok-4` über `langchain-xai` (`ChatXAI`, Key `XAI_API_KEY`).

## Struktur

```text
main.py                  CLI
grok_agents/state.py     AgentState (TypedDict)
grok_agents/llm.py       ChatXAI
grok_agents/tools.py     Tool-Definition web_search
grok_agents/agents.py    Planner, Researcher, Synthesizer
grok_agents/graph.py     StateGraph und Tool-Schleife
```

## Installation

```bash
cd grok-multi-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

In `.env` den Key von [console.x.ai](https://console.x.ai/) eintragen:

```text
XAI_API_KEY=xai-...
```

## Start

Im Terminal, von überall:

```bash
multigrok "Was ist LangGraph?"
```

Im Finder geht auch ein Doppelklick auf `Start.command`. Oder diese eine Zeile:

```bash
/Users/user/grok-multi-agent/.venv/bin/python /Users/user/grok-multi-agent/main.py "Was ist LangGraph?"
```

Ohne Argument kommt eine kurze Standardfrage. Zuerst erscheint „Läuft…“, die Antwort kommt etwa eine Minute später.

## Tool-Calling

Die Tool-Definition steht in `grok_agents/tools.py`: eine normale Funktion mit `@tool`. Die Beschreibung im Docstring sieht das Modell.

Der Researcher bindet sie an Grok. `ToolNode` führt den Call aus. Die Kante zurück zum Researcher steht in `grok_agents/graph.py`:

```python
llm = llm.bind_tools([web_search], tool_choice=tool_choice)

graph.add_node("tools", run_tools)  # run_tools ruft ToolNode([web_search])
graph.add_conditional_edges(
    "researcher",
    route_after_researcher,  # tool_calls? → "tools", sonst → "synthesizer"
    {"tools": "tools", "synthesizer": "synthesizer"},
)
graph.add_edge("tools", "researcher")
```

Nach drei Suchen bekommt der Researcher das Tool nicht mehr und muss die Notizen schreiben.
