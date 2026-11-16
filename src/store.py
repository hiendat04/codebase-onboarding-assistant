from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src import config


def get_store(embeddings: Embeddings | None = None, persist_dir: Path | None = None) -> Chroma:
    if embeddings is None:  # imported here so tests with fake embeddings never load the model
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBED_MODEL,
                                           encode_kwargs={"normalize_embeddings": True})
    return Chroma(collection_name=config.COLLECTION, embedding_function=embeddings,
                  persist_directory=str(persist_dir or config.CHROMA_DIR),
                  collection_metadata={"hnsw:space": "cosine"})


def search(store: Chroma, query: str, k: int = config.TOP_K) -> list[Document]:
    return store.similarity_search(config.QUERY_PREFIX + query, k=k)
