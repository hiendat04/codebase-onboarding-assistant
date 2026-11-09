from src.config import MAX_CHARS, OVERLAP_LINES
from src.models import make_id, split_long


def test_make_id_is_stable_and_distinct():
    a = make_id("kubernetes", "pkg/a.go", 1, 10)
    assert len(a) == 40
    assert a == make_id("kubernetes", "pkg/a.go", 1, 10)
    assert a != make_id("kubernetes", "pkg/a.go", 1, 11)


def test_split_long_short_text_is_one_window():
    assert split_long(["a", "b"], 10) == [("a\nb", 10, 11)]


def test_split_long_windows_overlap_and_fit():
    windows = split_long(["x" * 100] * 200, 1)
    assert len(windows) > 1
    assert all(len(text) <= MAX_CHARS for text, _, _ in windows)
    assert windows[1][1] == windows[0][2] - OVERLAP_LINES + 1
    assert windows[-1][2] == 200


def test_split_long_hard_cuts_huge_line():
    windows = split_long(["x" * 50000], 1)
    assert len(windows) == 1
    assert len(windows[0][0]) == MAX_CHARS
