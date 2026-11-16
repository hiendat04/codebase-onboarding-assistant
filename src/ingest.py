import json
import random
import statistics
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from src import config
from src.chunk_go import chunk_go
from src.chunk_md import chunk_markdown
from src.files import list_files
from src.models import Chunk


def ingest_all() -> list[Chunk]:
    """Chunk the Go code and docs in scope; `path` is relative to each repo's folder."""
    k8s, community = config.REPOS["kubernetes"]["dir"], config.REPOS["community"]["dir"]
    chunks: list[Chunk] = []
    for f in list_files(k8s, config.SUBSYSTEMS, (".go",)):
        chunks += chunk_go("kubernetes", f.relative_to(k8s).as_posix(), f.read_bytes())
    for repo, root, subdirs in [("kubernetes", k8s, config.SUBSYSTEMS), ("community", community, config.DOC_DIRS)]:
        for f in list_files(root, subdirs, (".md",)):
            chunks += chunk_markdown(repo, f.relative_to(root).as_posix(), f.read_bytes().decode(errors="replace"))
    return chunks


def save_chunks(chunks: list[Chunk], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for c in chunks:
            f.write(json.dumps(asdict(c)) + "\n")


if __name__ == "__main__":
    chunks = ingest_all()
    save_chunks(chunks, config.CHUNKS_FILE)
    sizes = [len(c.text) for c in chunks]
    print(f"{len(chunks)} chunks -> {config.CHUNKS_FILE}")
    print("by kind:", dict(Counter(c.kind for c in chunks)))
    print(f"size min/median/max: {min(sizes)} / {int(statistics.median(sizes))} / {max(sizes)}")
    random.seed(0)
    for c in random.sample(chunks, 10):
        print(f"\n{c.repo} {c.path}:{c.start_line}-{c.end_line} {c.symbol}\n{c.text[:200]}")
