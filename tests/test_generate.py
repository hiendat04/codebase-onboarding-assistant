import json

from src.evaluation.generate import generate_answers
from tests.test_rag import recording_llm, store_with

QUESTIONS = [{"id": f"q{i}", "question": f"question {i}", "reference": "ref", "type": "how"} for i in range(2)]


def test_writes_one_row_per_question_with_contexts(tmp_path):
    llm, _ = recording_llm("ans")
    out = tmp_path / "answers.jsonl"
    assert generate_answers(QUESTIONS, out, store_with(tmp_path / "db", 3), llm) == 2
    rows = [json.loads(line) for line in out.open()]
    assert [r["id"] for r in rows] == ["q0", "q1"]
    assert rows[0]["rag_answer"] == rows[0]["baseline_answer"] == "ans"
    assert len(rows[0]["contexts"]) == 3 and "text" in rows[0]["contexts"][0]


def test_second_run_skips_cached_ids(tmp_path):
    llm, seen = recording_llm()
    out, store = tmp_path / "answers.jsonl", store_with(tmp_path / "db", 1)
    generate_answers(QUESTIONS[:1], out, store, llm)
    calls = len(seen)
    assert generate_answers(QUESTIONS, out, store, llm) == 1
    assert len(seen) == calls + 2  # only q1 was answered (rag + baseline)
    assert len(out.read_text().splitlines()) == 2
