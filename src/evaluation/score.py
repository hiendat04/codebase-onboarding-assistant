import argparse
import json

import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from ragas import EvaluationDataset, RunConfig, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (AnswerCorrectness, AnswerRelevancy, Faithfulness,
                           LLMContextPrecisionWithReference, LLMContextRecall)

from src import config

SHARED = [AnswerCorrectness, AnswerRelevancy]  # both systems: the main comparison
RAG_ONLY = [Faithfulness, LLMContextPrecisionWithReference, LLMContextRecall]  # need contexts


def score(rows: list[dict], system: str) -> pd.DataFrame:
    if system == "rag":
        samples = [{"user_input": r["question"], "response": r["rag_answer"], "reference": r["reference"],
                    "retrieved_contexts": r["contexts"]} for r in rows]
        metrics = SHARED + RAG_ONLY
    else:
        samples = [{"user_input": r["question"], "response": r["baseline_answer"], "reference": r["reference"]}
                   for r in rows]
        metrics = SHARED
    result = evaluate(
        EvaluationDataset.from_list(samples),
        metrics=[m() for m in metrics],
        llm=LangchainLLMWrapper(ChatOllama(model=config.JUDGE_MODEL, temperature=0)),
        embeddings=LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(
            model_name=config.EMBED_MODEL, encode_kwargs={"normalize_embeddings": True})),
        run_config=RunConfig(timeout=900, max_workers=2),  # a local judge is slow; don't overload it
    )
    df = result.to_pandas()
    df.insert(0, "system", system)
    df.insert(0, "type", [r["type"] for r in rows])
    df.insert(0, "id", [r["id"] for r in rows])
    return df.drop(columns=["user_input", "response", "reference", "retrieved_contexts"], errors="ignore")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="dev", choices=["dev", "test"])
    split = parser.parse_args().split

    rows = [json.loads(line) for line in (config.RESULTS_DIR / f"answers_{split}.jsonl").open() if line.strip()]
    parts = []
    for system in ("baseline", "rag"):
        cache = config.RESULTS_DIR / f"scores_{split}_{system}.csv"
        if not cache.exists():  # each system is a long run; keep it once it's done
            score(rows, system).to_csv(cache, index=False)
        parts.append(pd.read_csv(cache))
    df = pd.concat(parts, ignore_index=True)
    out = config.RESULTS_DIR / f"scores_{split}.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} rows -> {out}")
    print(df.drop(columns=["id", "type"]).groupby("system").mean().round(3))
