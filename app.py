import httpx
import streamlit as st

from src.generation.llm import get_llm
from src.generation.prompts import cite, link_citations, permalink
from src.generation.rag import answer_baseline, answer_rag
from src.retrieval.store import get_store


@st.cache_resource  # load the embedding model, Chroma and the LLM once, not on every click
def resources():
    return get_store(), get_llm()


st.set_page_config(page_title="Kubernetes Onboarding Assistant")
st.title("Kubernetes Onboarding Assistant")
st.caption("Ask about the scheduler, kubelet, client-go or the contributor docs.")

question = st.text_input("Question", placeholder="Which function in the scheduler picks the node for a pod?")
show_baseline = st.checkbox("Show baseline (same LLM, no retrieval)")

if st.button("Ask", type="primary") and question.strip():
    store, llm = resources()
    try:
        with st.spinner("Thinking..."):
            answer, docs = answer_rag(question, store, llm)
            baseline = answer_baseline(question, llm) if show_baseline else None
    except (ConnectionError, httpx.ConnectError):
        st.error("Ollama is not running: start it with 'ollama serve'")
        st.stop()

    rag_col, base_col = st.columns(2) if show_baseline else (st.container(), None)
    with rag_col:
        st.subheader("RAG")
        st.markdown(link_citations(answer, docs))
    if base_col:
        with base_col:
            st.subheader("Baseline")
            st.markdown(baseline)

    with st.expander(f"Retrieved chunks ({len(docs)})"):
        for d in docs:
            st.markdown(f"**[{cite(d.metadata)}]({permalink(d.metadata)})** · `{d.metadata['symbol']}`")
            st.code(d.page_content, language="go" if d.metadata["kind"] == "code" else "markdown")
