from src.evaluation.retrieval import hit_at_k, reciprocal_rank

GOLD = ["pkg/a.go"]


def test_hit_inside_k():
    paths = ["x.go", "pkg/a.go", "y.go"]
    assert hit_at_k(paths, GOLD, 2) == 1
    assert reciprocal_rank(paths, GOLD) == 0.5


def test_hit_just_outside_k():
    assert hit_at_k(["x.go", "y.go", "pkg/a.go"], GOLD, 2) == 0


def test_miss_is_zero():
    assert hit_at_k(["x.go"], GOLD, 16) == 0
    assert reciprocal_rank(["x.go"], GOLD) == 0.0


def test_repeated_gold_file_uses_first_rank():
    assert reciprocal_rank(["x.go", "pkg/a.go", "pkg/a.go"], GOLD) == 0.5
