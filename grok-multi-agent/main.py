"""Start: /Users/jorzcanjo/grok-multi-agent/Start.command """

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grok_agents.graph import build_graph


def main() -> int:
    load_dotenv(ROOT / ".env")
    if not os.environ.get("XAI_API_KEY"):
        print("XAI_API_KEY fehlt. Kopiere .env.example nach .env und setze den Key.")
        return 1

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = "Was ist LangGraph, und wer entwickelt es?"

    print("Läuft. Planner, Suche und Antwort dauern etwa eine Minute.", flush=True)
    result = build_graph().invoke(
        {
            "question": question,
            "plan": "",
            "messages": [],
            "notes": "",
            "answer": "",
            "tool_rounds": 0,
        },
        config={"recursion_limit": 15},
    )

    print("\n## Plan\n")
    print(result["plan"])
    print("\n## Suche\n")
    saw_call = False
    for message in result["messages"]:
        for call in getattr(message, "tool_calls", None) or []:
            saw_call = True
            args = call.get("args") or {}
            print(f"- {call.get('name')}({args.get('query', args)})")
    if not saw_call:
        print("(kein Tool-Call)")
    print("\n## Antwort\n")
    print(result["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
