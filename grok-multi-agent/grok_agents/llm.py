from langchain_xai import ChatXAI

# Alias aus der langchain-xai Doku. ChatXAI liest XAI_API_KEY aus der Umgebung.
MODEL = "grok-4"


def make_llm() -> ChatXAI:
    return ChatXAI(model=MODEL, temperature=0)
