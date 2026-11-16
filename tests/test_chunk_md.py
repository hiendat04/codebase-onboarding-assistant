from src.chunk_md import chunk_markdown


def chunks(text, path="docs/readme.md"):
    return chunk_markdown("community", path, text)


def test_split_by_heading_with_path_and_lines():
    got = chunks("# A\nintro\n## B\nbody\n# C\nmore\n")
    assert [(c.symbol, c.start_line, c.end_line) for c in got] == [
        ("A", 1, 2), ("A > B", 3, 4), ("C", 5, 6)]
    assert got[0].kind == "doc" and got[0].repo == "community" and got[0].text == "# A\nintro"


def test_hash_inside_code_fence_is_not_a_heading():
    got = chunks("# A\n```bash\n# comment\nls\n```\nafter\n")
    assert len(got) == 1
    assert "# comment" in got[0].text


def test_text_before_first_heading():
    assert [c.symbol for c in chunks("intro\n# A\nbody\n")] == ["readme.md", "A"]


def test_no_headings_gives_one_chunk():
    got = chunks("just text\nmore\n")
    assert [c.symbol for c in got] == ["readme.md"]


def test_heading_only_section_is_dropped():
    assert [c.symbol for c in chunks("# A\n# B\ntext\n")] == ["B"]


def test_empty_text_returns_empty_list():
    assert chunks("") == []
