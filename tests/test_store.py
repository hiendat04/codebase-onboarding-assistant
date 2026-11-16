from langchain_core.embeddings import DeterministicFakeEmbedding

from src.store import get_store, search

fake = DeterministicFakeEmbedding(size=16)


def test_search_empty_store_returns_empty_list(tmp_path):
    assert search(get_store(fake, tmp_path), "anything") == []


def test_search_returns_k_documents_with_metadata(tmp_path):
    store = get_store(fake, tmp_path)
    store.add_texts(["a", "b", "c"], metadatas=[{"path": p} for p in "xyz"], ids=["1", "2", "3"])
    docs = search(store, "q", k=2)
    assert len(docs) == 2
    assert all("path" in d.metadata for d in docs)


def test_store_persists_between_instances(tmp_path):
    get_store(fake, tmp_path).add_texts(["a"], metadatas=[{"path": "x"}], ids=["1"])
    assert len(search(get_store(fake, tmp_path), "q")) == 1
