from langchain_ollama import ChatOllama

from src import config


def get_llm() -> ChatOllama:
    return ChatOllama(model=config.LLM_MODEL, temperature=0)
