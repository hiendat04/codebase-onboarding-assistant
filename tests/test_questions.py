from src.evaluation.questions import load_questions, validate

INDEXED = {"pkg/scheduler/schedule_one.go"}


def good_row(**overrides):
    row = {"id": "sched-01", "question": "Where is the node picked?", "reference": "schedulePod.",
           "gold_paths": ["pkg/scheduler/schedule_one.go"], "type": "where", "split": "dev"}
    return {**row, **overrides}


def test_valid_rows_have_no_errors():
    assert validate([good_row(), good_row(id="sched-02")], INDEXED) == []


def test_unindexed_gold_path_is_rejected():
    errors = validate([good_row(gold_paths=["pkg/nope.go"])], INDEXED)
    assert len(errors) == 1 and "sched-01" in errors[0] and "pkg/nope.go" in errors[0]


def test_duplicate_id_is_rejected():
    errors = validate([good_row(), good_row()], INDEXED)
    assert len(errors) == 1 and "duplicate" in errors[0]


def test_bad_type_and_split_are_rejected():
    errors = validate([good_row(type="wher", split="train")], INDEXED)
    assert len(errors) == 2
    assert any("type" in e for e in errors) and any("split" in e for e in errors)


def test_missing_field_is_rejected():
    row = good_row()
    del row["reference"]
    errors = validate([row], INDEXED)
    assert len(errors) == 1 and "reference" in errors[0]


def test_load_skips_blank_lines(tmp_path):
    f = tmp_path / "q.jsonl"
    f.write_text('{"id": "a"}\n\n{"id": "b"}\n\n')
    assert [q["id"] for q in load_questions(f)] == ["a", "b"]
