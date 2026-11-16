import sys

import httpx

from src.generation.prompts import cite, permalink
from src.generation.rag import answer_baseline, answer_rag

if __name__ == "__main__":
    question = sys.argv[1]
    try:
        answer, docs = answer_rag(question)
        baseline = answer_baseline(question)
    except (ConnectionError, httpx.ConnectError):
        sys.exit("Ollama is not running: start it with 'ollama serve'")
    print("=== RAG ===\n" + answer)
    print("\n=== Sources ===")
    for d in docs:
        print(f"{cite(d.metadata)} -> {permalink(d.metadata)}")
    print("\n=== Baseline ===\n" + baseline)
