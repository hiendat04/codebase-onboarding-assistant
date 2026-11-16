import hashlib
from dataclasses import dataclass

from src.config import MAX_CHARS, OVERLAP_LINES


@dataclass
class Chunk:
    id: str
    text: str
    repo: str
    path: str  # relative to the repo root
    start_line: int  # 1-based, inclusive
    end_line: int
    symbol: str
    kind: str  # "code" or "doc"


def make_id(repo: str, path: str, start_line: int, end_line: int) -> str:
    return hashlib.sha1(f"{repo}:{path}:{start_line}:{end_line}".encode()).hexdigest()


def split_long(lines: list[str], first_line: int) -> list[tuple[str, int, int]]:
    """Cut lines into windows of at most MAX_CHARS, overlapping by OVERLAP_LINES.

    Returns (text, start_line, end_line); `lines[0]` is line `first_line`.
    """
    lines = [line[:MAX_CHARS] for line in lines]  # a single huge line is hard-cut
    windows, start = [], 0
    while start < len(lines):
        end, size = start, len(lines[start])
        while end + 1 < len(lines) and size + 1 + len(lines[end + 1]) <= MAX_CHARS:
            end += 1
            size += 1 + len(lines[end])
        windows.append(("\n".join(lines[start:end + 1]), first_line + start, first_line + end))
        if end == len(lines) - 1:
            break
        start = max(end - OVERLAP_LINES + 1, start + 1)  # always advance, or we loop forever
    return windows
