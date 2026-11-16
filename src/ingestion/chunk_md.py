import re

from src.ingestion.models import Chunk, make_id, split_long

_HEADING = re.compile(r"^(#{1,6}) +(.*\S)\s*$")


def chunk_markdown(repo: str, path: str, text: str) -> list[Chunk]:
    """One chunk per heading section; symbol is the heading path ("A > B")."""
    lines = text.split("\n")
    filename = path.rsplit("/", 1)[-1]
    chunks: list[Chunk] = []

    def emit(start: int, end: int, symbol: str, has_heading: bool) -> None:  # rows, end exclusive
        section = lines[start:end]
        while section and not section[-1].strip():
            section.pop()
        if not any(line.strip() for line in section[has_heading:]):  # heading-only or blank
            return
        for body, s, e in split_long(section, start + 1):
            chunks.append(Chunk(make_id(repo, path, s, e), body, repo, path, s, e, symbol, "doc"))

    stack: list[tuple[int, str]] = []  # heading path as (level, title)
    start, symbol, has_heading, in_fence = 0, filename, False, False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else _HEADING.match(line)
        if match:
            emit(start, i, symbol, has_heading)
            level = len(match[1])
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, match[2]))
            start, symbol, has_heading = i, " > ".join(t for _, t in stack), True
    emit(start, len(lines), symbol, has_heading)
    return chunks
