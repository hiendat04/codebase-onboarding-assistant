from urllib.parse import quote

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from src import config

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are helping a new engineer understand the Kubernetes codebase.\n"
     "Rules:\n"
     "1. Answer only from the context below. Do not use outside knowledge.\n"
     "2. Cite every claim with the label of the chunk it came from, exactly as written, e.g. [pkg/a.go:10-20].\n"
     "3. If the context does not contain the answer, reply exactly: not found in context\n\n"
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
