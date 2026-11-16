import dataclasses
import json

from src.ingestion.ingest import save_chunks
from src.ingestion.models import Chunk


def test_save_chunks_roundtrip(tmp_path):
    chunks = [Chunk("id1", "text one", "kubernetes", "pkg/a.go", 1, 3, "Foo", "code"),
              Chunk("id2", "text two", "community", "docs/b.md", 5, 9, "B", "doc")]
    out = tmp_path / "chunks.jsonl"
    save_chunks(chunks, out)
    lines = out.read_text().splitlines()
    assert len(lines) == 2
    assert [json.loads(line) for line in lines] == [dataclasses.asdict(c) for c in chunks]
