from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.generation.rag import answer_baseline, answer_rag
from src.ingestion.models import Chunk
from src.retrieval.index import index_chunks
from src.retrieval.store import get_store


def recording_llm(reply="fake answer"):
    """Fake LLM that returns `reply` and remembers the prompt text it was given."""
    seen = []

    def call(prompt):
        seen.append(prompt.to_string())
        return AIMessage(reply)
    return RunnableLambda(call), seen


def store_with(tmp_path, n):
    store = get_store(DeterministicFakeEmbedding(size=16), tmp_path)
    index_chunks([Chunk(f"c{i}", f"text {i}", "kubernetes", f"pkg/f{i}.go", 1, 2, f"F{i}", "code")
                  for i in range(n)], store)
    return store


def test_answer_rag_returns_answer_and_retrieved_docs(tmp_path):
    llm, _ = recording_llm()
    answer, docs = answer_rag("q", store_with(tmp_path, 3), llm)
    assert answer == "fake answer"
    assert len(docs) == 3


def test_answer_rag_puts_context_in_prompt(tmp_path):
    llm, seen = recording_llm()
    answer_rag("where is F0?", store_with(tmp_path, 1), llm)
    assert "[pkg/f0.go:1-2]" in seen[0]
    assert "where is F0?" in seen[0]


def test_answer_rag_empty_store(tmp_path):
    llm, _ = recording_llm("not found in context")
    assert answer_rag("q", store_with(tmp_path, 0), llm) == ("not found in context", [])


def test_answer_baseline_has_no_context():
    llm, seen = recording_llm()
    assert answer_baseline("how does kubelet work?", llm) == "fake answer"
    assert "how does kubelet work?" in seen[0]
    assert "[" not in seen[0]
