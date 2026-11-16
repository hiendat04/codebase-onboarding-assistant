from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel

from src.generation.llm import get_llm
from src.generation.prompts import BASELINE_PROMPT, RAG_PROMPT, format_context
from src.retrieval.store import get_store, search


def answer_rag(question: str, store: Chroma | None = None,
               llm: BaseChatModel | None = None) -> tuple[str, list[Document]]:
    """Answer from the retrieved chunks; returns (answer, retrieved docs)."""
    docs = search(store or get_store(), question)
    reply = (RAG_PROMPT | (llm or get_llm())).invoke({"context": format_context(docs), "question": question})
    return reply.content, docs


def answer_baseline(question: str, llm: BaseChatModel | None = None) -> str:
    """Answer from the LLM alone, with no retrieval."""
    return (BASELINE_PROMPT | (llm or get_llm())).invoke({"question": question}).content
