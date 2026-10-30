from ddgs import DDGS
from langchain_core.tools import tool

# Der Researcher darf höchstens so oft suchen, dann muss er Notizen schreiben.
MAX_TOOL_ROUNDS = 3


@tool
def web_search(query: str) -> str:
    """Suche im Web über DuckDuckGo.

    Nutze das Tool für Fakten, Namen, Daten und Quellen.
    query ist eine kurze Suchanfrage, keine ganze Frage mit mehreren Teilen.
    """
    try:
        results = DDGS().text(
            query,
            max_results=5,
            region="de-de",
            backend="duckduckgo",
        )
    except Exception as exc:  # Netzwerk oder Rate-Limit: der Agent soll das sehen.
        return f"Suche fehlgeschlagen: {exc}"

    if not results:
        return "Keine Treffer."

    blocks: list[str] = []
    for index, item in enumerate(results, start=1):
        title = str(item.get("title") or "").strip()
        href = str(item.get("href") or "").strip()
        body = " ".join(str(item.get("body") or "").split())
        if len(body) > 300:
            body = body[:300] + "…"
        blocks.append(f"{index}. {title}\n{href}\n{body}")
    return "\n\n".join(blocks)
