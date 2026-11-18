import json
import sys
from collections import Counter
from pathlib import Path

from src import config

FIELDS = ["id", "question", "reference", "gold_paths", "type", "split"]
TYPES = {"where", "how", "interaction", "docs"}
SPLITS = {"dev", "test"}
QUESTIONS_FILE = config.ROOT / "eval" / "questions.jsonl"


def load_questions(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def validate(questions: list[dict], indexed_paths: set[str]) -> list[str]:
    """Return one error message per problem; an empty list means the set is valid."""
    errors, seen = [], set()
    for n, q in enumerate(questions, 1):
        name = q.get("id") or f"line {n}"
        if missing := [f for f in FIELDS if f not in q]:
            errors.append(f"{name}: missing fields {missing}")
            continue
        if q["id"] in seen:
            errors.append(f"{name}: duplicate id")
        seen.add(q["id"])
        for field in ("question", "reference"):
            if not str(q[field]).strip():
                errors.append(f"{name}: empty {field}")
        if not isinstance(q["gold_paths"], list) or not q["gold_paths"]:
            errors.append(f"{name}: gold_paths must be a non-empty list")
        else:
            errors += [f"{name}: gold path not indexed: {p}" for p in q["gold_paths"] if p not in indexed_paths]
        if q["type"] not in TYPES:
            errors.append(f"{name}: type {q['type']!r} not in {sorted(TYPES)}")
        if q["split"] not in SPLITS:
            errors.append(f"{name}: split {q['split']!r} not in {sorted(SPLITS)}")
    return errors


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else QUESTIONS_FILE
    questions = load_questions(path)
    with config.CHUNKS_FILE.open() as f:
        indexed = {json.loads(line)["path"] for line in f}
    errors = validate(questions, indexed)
    print("\n".join(errors) or "OK")
    print(f"{len(questions)} questions")
    print("by type:", dict(Counter(q.get("type") for q in questions)))
    print("by split:", dict(Counter(q.get("split") for q in questions)))
    sys.exit(1 if errors else 0)
