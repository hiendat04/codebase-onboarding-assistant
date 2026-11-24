import argparse
import json
from pathlib import Path

from src import config
from src.evaluation.questions import QUESTIONS_FILE, load_questions
from src.generation.llm import get_llm
from src.generation.prompts import cite
from src.generation.rag import answer_baseline, answer_rag
from src.retrieval.store import get_store


def generate_answers(questions: list[dict], out: Path, store=None, llm=None) -> int:
    """Answer each question with RAG and baseline, appending to `out`; ids already in `out` are skipped."""
    done = {json.loads(line)["id"] for line in out.open() if line.strip()} if out.exists() else set()
    todo = [q for q in questions if q["id"] not in done]
    store, llm = store or get_store(), llm or get_llm()
    with out.open("a") as f:
        for n, q in enumerate(todo, 1):
            answer, docs = answer_rag(q["question"], store, llm)
            row = {"id": q["id"], "question": q["question"], "reference": q["reference"], "type": q["type"],
                   "rag_answer": answer,
                   "contexts": [f"[{cite(d.metadata)}]\n{d.page_content}" for d in docs],
                   "baseline_answer": answer_baseline(q["question"], llm)}
            f.write(json.dumps(row) + "\n")
            f.flush()  # keep finished rows if the run is stopped       
            print(f"{n}/{len(todo)} {q['id']}")
    return len(todo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="dev", choices=["dev", "test"])
    split = parser.parse_args().split

    questions = [q for q in load_questions(QUESTIONS_FILE) if q["split"] == split]
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.RESULTS_DIR / f"answers_{split}.jsonl"
    added = generate_answers(questions, out)
    print(f"added {added}, {len(questions)} {split} questions in {out}")
