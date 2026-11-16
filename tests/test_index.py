from langchain_core.embeddings import DeterministicFakeEmbedding

from src.retrieval.index import index_chunks, load_chunks
from src.ingestion.ingest import save_chunks
from src.ingestion.models import Chunk
from src.retrieval.store import get_store


def make_chunks(n):
    return [Chunk(f"c{i}", f"text {i}", "kubernetes", f"pkg/f{i}.go", 1, 2, f"F{i}", "code") for i in range(n)]


def store_at(tmp_path):
    return get_store(DeterministicFakeEmbedding(size=16), tmp_path)


def test_index_adds_all_with_exact_metadata(tmp_path):
    store = store_at(tmp_path)
    assert index_chunks(make_chunks(5), store, batch_size=2) == 5
    got = store.get(ids=["c0"])
    assert len(store.get()["ids"]) == 5
    assert got["metadatas"][0] == {"repo": "kubernetes", "path": "pkg/f0.go", "start_line": 1,
                                   "end_line": 2, "symbol": "F0", "kind": "code"}


def test_second_run_adds_nothing(tmp_path):
    store = store_at(tmp_path)
    index_chunks(make_chunks(5), store)
    assert index_chunks(make_chunks(5), store) == 0
    assert len(store.get()["ids"]) == 5


def test_resume_adds_only_missing(tmp_path):
    store = store_at(tmp_path)
    index_chunks(make_chunks(3), store)
    assert index_chunks(make_chunks(5), store) == 2
    assert len(store.get()["ids"]) == 5


def test_empty_list_returns_zero(tmp_path):
    assert index_chunks([], store_at(tmp_path)) == 0


def test_load_chunks_roundtrip(tmp_path):
    chunks = make_chunks(3)
    save_chunks(chunks, tmp_path / "c.jsonl")
    assert load_chunks(tmp_path / "c.jsonl") == chunks
