import json
from pathlib import Path

from langchain_chroma import Chroma

from src import config
from src.models import Chunk
from src.store import get_store


def load_chunks(path: Path) -> list[Chunk]:
    with path.open() as f:
        return [Chunk(**json.loads(line)) for line in f]


def index_chunks(chunks: list[Chunk], store: Chroma, batch_size: int = 256) -> int:
    """Add chunks not already in the store; return how many were added."""
    existing = set(store.get(include=[])["ids"])
    todo = [c for c in chunks if c.id not in existing]
    for i in range(0, len(todo), batch_size):
        batch = todo[i:i + batch_size]
        store.add_texts(
            [c.text for c in batch],
            metadatas=[{"repo": c.repo, "path": c.path, "start_line": c.start_line,
                        "end_line": c.end_line, "symbol": c.symbol, "kind": c.kind} for c in batch],
            ids=[c.id for c in batch],
        )
        print(f"indexed {i + len(batch)}/{len(todo)}")
    return len(todo)


if __name__ == "__main__":
    store = get_store()
    added = index_chunks(load_chunks(config.CHUNKS_FILE), store)
    print(f"added {added}, total {len(store.get(include=[])['ids'])}")
