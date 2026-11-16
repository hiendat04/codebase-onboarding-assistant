import tree_sitter_go
from tree_sitter import Language, Node, Parser

from src.models import Chunk, make_id, split_long

_parser = Parser(Language(tree_sitter_go.language()))
_DECLS = ("function_declaration", "method_declaration", "type_declaration")


def _find(node: Node, type_: str) -> Node | None:
    if node.type == type_:
        return node
    for child in node.children:
        if (hit := _find(child, type_)) is not None:
            return hit
    return None


def _name(node: Node) -> str:
    field = node.child_by_field_name("name")
    return field.text.decode(errors="replace") if field else "<unknown>"


def _symbol(node: Node) -> str:
    if node.type == "function_declaration":
        return _name(node)
    if node.type == "method_declaration":
        receiver = node.child_by_field_name("receiver")
        recv_type = _find(receiver, "type_identifier") if receiver else None
        recv = recv_type.text.decode(errors="replace") if recv_type else "?"
        return f"{recv}.{_name(node)}"
    specs = [_name(c) for c in node.children if c.type in ("type_spec", "type_alias")]
    return ", ".join(specs) or "<type>"


def chunk_go(repo: str, path: str, source: bytes) -> list[Chunk]:
    """One chunk per top-level func/method/type (with its doc comment); other top-level code
    (package, imports, const, var) goes into chunks of consecutive leftover nodes."""
    lines = source.decode(errors="replace").split("\n")
    tree = _parser.parse(source)  # keep a reference: nodes point into the tree and crash if it is freed
    children = tree.root_node.children
    pkg_node = next((c for c in children if c.type == "package_clause"), None)
    pkg = _find(pkg_node, "package_identifier") if pkg_node else None
    pkg_name = pkg.text.decode(errors="replace") if pkg else ""

    chunks: list[Chunk] = []

    def emit(symbol: str, start: int, end: int) -> None:  # start/end: 0-based rows, inclusive
        header = f"// file: {path}  package: {pkg_name}  symbol: {symbol}\n"
        for text, s, e in split_long(lines[start:end + 1], start + 1):
            chunks.append(Chunk(make_id(repo, path, s, e), header + text, repo, path, s, e, symbol, "code"))

    run: list[Node] = []  # consecutive leftover nodes

    def flush() -> None:
        if run:
            symbol = "<file header>" if any(n.type == "package_clause" for n in run) else "<declarations>"
            emit(symbol, run[0].start_point.row, run[-1].end_point.row)
            run.clear()

    for i, node in enumerate(children):
        if node.type not in _DECLS:
            # a trailing comment on a line already covered by the previous node adds nothing
            if not (node.type == "comment" and i > 0 and node.start_point.row == children[i - 1].end_point.row):
                run.append(node)
            continue
        # pull directly preceding comments (on their own lines) into this declaration
        first = i
        while (first > 0 and children[first - 1].type == "comment"
               and children[first - 1].end_point.row == children[first].start_point.row - 1
               and (first == 1 or children[first - 2].end_point.row < children[first - 1].start_point.row)):
            first -= 1
            if run and run[-1] is children[first]:
                run.pop()
        flush()
        emit(_symbol(node), children[first].start_point.row, node.end_point.row)
    flush()
    return chunks
