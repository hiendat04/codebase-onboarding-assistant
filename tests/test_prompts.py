from langchain_core.documents import Document

from src import config
from src.generation.prompts import BASELINE_PROMPT, RAG_PROMPT, cite, format_context, link_citations, permalink

META = {"repo": "kubernetes", "path": "pkg/a.go", "start_line": 3, "end_line": 9}


def test_cite_label():
    assert cite(META) == "pkg/a.go:3-9"


def test_format_context_labels_each_chunk():
    docs = [Document("func A() {}", metadata=META),
            Document("func B() {}", metadata={**META, "path": "pkg/b.go"})]
    text = format_context(docs)
    assert "[pkg/a.go:3-9]\nfunc A() {}" in text
    assert "[pkg/b.go:3-9]" in text


def test_format_context_empty():
    assert format_context([]) == ""


def test_permalink_kubernetes():
    assert permalink(META) == f"https://github.com/kubernetes/kubernetes/blob/{config.K8S_SHA}/pkg/a.go#L3-L9"


def test_permalink_community_uses_community_sha():
    url = permalink({**META, "repo": "community", "path": "contributors/devel/README.md"})
    assert "kubernetes/community/blob/" in url and config.COMMUNITY_SHA in url


def test_permalink_quotes_path():
    assert "my%20file.md" in permalink({**META, "path": "docs/my file.md"})


def test_prompts_have_expected_variables():
    assert set(RAG_PROMPT.input_variables) == {"context", "question"}
    assert BASELINE_PROMPT.input_variables == ["question"]


DOC = Document("x", metadata={"repo": "kubernetes", "path": "pkg/a.go", "start_line": 3, "end_line": 9})
LINK = f"[pkg/a.go:3-9]({permalink(DOC.metadata)})"


def test_link_citations_bracketed_and_backticked():
    assert link_citations("see [pkg/a.go:3-9].", [DOC]) == f"see {LINK}."
    assert link_citations("see `pkg/a.go:3-9`.", [DOC]) == f"see {LINK}."


def test_link_citations_leaves_unretrieved_label_alone():
    text = "see [pkg/b.go:1-2] and [pkg/a.go:3-90]"
    assert link_citations(text, [DOC]) == text


def test_link_citations_repeated_label():
    assert link_citations("[pkg/a.go:3-9] and pkg/a.go:3-9", [DOC]) == f"{LINK} and {LINK}"
