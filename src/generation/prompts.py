import re
from urllib.parse import quote

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from src import config

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are helping a new engineer understand the Kubernetes codebase.\n"
     "Give a complete, explanatory answer, like a senior engineer walking a newcomer through the code:\n"
     "- Start with a one-sentence direct answer, then explain how it works step by step.\n"
     "- Name the exact functions, types, files, constants and their values as they appear in the code.\n"
     "- Use short paragraphs or a bulleted list; quote a few key lines of code if it helps.\n"
     "Rules:\n"
     "1. Use only the context below. Do not use outside knowledge.\n"
     "2. After each claim, cite the label of the chunk it came from, exactly as written, e.g. [pkg/a.go:10-20].\n"
     "3. If the context does not contain the answer at all, reply exactly: not found in context\n\n"
     "Context:\n{context}"),
    ("human", "{question}"),
])

BASELINE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a Kubernetes expert helping a new engineer understand the Kubernetes codebase."),
    ("human", "{question}"),
])

_SHAS = {"kubernetes": config.K8S_SHA, "community": config.COMMUNITY_SHA}


def cite(metadata: dict) -> str:
    return f"{metadata['path']}:{metadata['start_line']}-{metadata['end_line']}"


def format_context(docs: list[Document]) -> str:
    return "\n\n".join(f"[{cite(d.metadata)}]\n{d.page_content}" for d in docs)


def permalink(metadata: dict) -> str:
    repo = metadata["repo"]
    return (f"https://github.com/kubernetes/{repo}/blob/{_SHAS[repo]}/{quote(metadata['path'])}"
            f"#L{metadata['start_line']}-L{metadata['end_line']}")


def link_citations(answer: str, docs: list[Document]) -> str:
    """Turn each retrieved chunk's label in the answer into a Markdown link; made-up labels stay plain."""
    for label, url in {cite(d.metadata): permalink(d.metadata) for d in docs}.items():
        pattern = rf"[\[`]?(?<![\w/.]){re.escape(label)}(?!\d)[\]`]?"
        answer = re.sub(pattern, lambda _: f"[{label}]({url})", answer)
    return answer
