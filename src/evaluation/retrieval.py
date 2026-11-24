import argparse

import pandas as pd

from src import config
from src.evaluation.questions import QUESTIONS_FILE, load_questions
from src.retrieval.store import get_store, search

KS = [4, 8, 16]


def hit_at_k(paths: list[str], gold: list[str], k: int) -> int:
    return int(any(p in gold for p in paths[:k]))


def reciprocal_rank(paths: list[str], gold: list[str]) -> float:
    return next((1 / i for i, p in enumerate(paths, 1) if p in gold), 0.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="dev", choices=["dev", "test"])
    split = parser.parse_args().split

    store = get_store()
    rows = []
    for q in load_questions(QUESTIONS_FILE):
        if q["split"] != split:
            continue
        paths = [d.metadata["path"] for d in search(store, q["question"], k=max(KS))]
        rr = reciprocal_rank(paths, q["gold_paths"])
        rows.append({"id": q["id"], "type": q["type"], "rank": round(1 / rr) if rr else None,
                     **{f"hit@{k}": hit_at_k(paths, q["gold_paths"], k) for k in KS}, "rr": rr})

    df = pd.DataFrame(rows)
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.RESULTS_DIR / f"retrieval_{split}.csv"
    df.to_csv(out, index=False)

    metrics = [f"hit@{k}" for k in KS] + ["rr"]
    print(f"{len(df)} {split} questions -> {out}")
    print("overall:", df[metrics].mean().round(3).to_dict())
    print(df.groupby("type")[metrics].mean().round(3).rename(columns={"rr": "mrr"}))
    print("misses at 16:", df.loc[df["hit@16"] == 0, "id"].tolist())
