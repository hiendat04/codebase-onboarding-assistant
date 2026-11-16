from src.chunk_go import chunk_go
from src.config import MAX_CHARS

SAMPLE = b"""package sched

import "fmt"

// Foo does foo.
// It is documented.
func Foo() {
	fmt.Println("x")
}

type Queue struct{}

func (q *Queue) Add() {}
"""


def chunks(src=SAMPLE):
    return chunk_go("kubernetes", "pkg/sched/a.go", src)


def test_one_chunk_per_declaration():
    assert [c.symbol for c in chunks()] == ["<file header>", "Foo", "Queue", "Queue.Add"]


def test_doc_comment_is_included_and_lines_are_exact():
    foo = chunks()[1]
    assert (foo.start_line, foo.end_line) == (5, 9)
    assert foo.text.startswith("// file: pkg/sched/a.go  package: sched  symbol: Foo\n// Foo does foo.")
    assert foo.kind == "code" and foo.repo == "kubernetes" and foo.path == "pkg/sched/a.go"


def test_chunk_ids_are_unique():
    ids = [c.id for c in chunks()]
    assert len(set(ids)) == len(ids)


def test_const_between_functions_is_own_chunk_with_exact_lines():
    src = b"package x\n\nfunc A() {}\n\nconst K = 1\n\nfunc B() {}\n"
    got = [(c.symbol, c.start_line, c.end_line) for c in chunks(src)]
    assert got == [("<file header>", 1, 1), ("A", 3, 3), ("<declarations>", 5, 5), ("B", 7, 7)]


def test_empty_source_returns_empty_list():
    assert chunks(b"") == []


def test_only_package_clause_gives_header_chunk():
    got = chunks(b"package x\n")
    assert [c.symbol for c in got] == ["<file header>"]


def test_invalid_utf8_does_not_crash():
    got = chunks(b'package x\n\nfunc Foo() {\n\ts := "\xff"\n\t_ = s\n}\n')
    assert "�" in got[1].text


def test_long_function_is_split():
    body = "\n".join(f"\tx{i} := {'1' * 30}" for i in range(400))
    got = [c for c in chunks(f"package x\n\nfunc Big() {{\n{body}\n}}\n".encode()) if c.symbol == "Big"]
    assert len(got) >= 2
    assert all(len(c.text) <= MAX_CHARS + 100 for c in got)


def test_trailing_comment_on_declaration_line_is_not_a_chunk():
    got = chunks(b"package x\n\ntype A int // note a\ntype B int // note b\n")
    assert [c.symbol for c in got] == ["<file header>", "A", "B"]
    assert len({c.id for c in got}) == len(got)
