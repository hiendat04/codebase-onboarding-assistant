import argparse

import matplotlib
import pandas as pd
from scipy.stats import wilcoxon

from src import config

matplotlib.use("Agg")  # write files only, no window
import matplotlib.pyplot as plt  # noqa: E402

SHARED = ["answer_correctness", "answer_relevancy"]


def paired_wilcoxon(scores: pd.DataFrame, metric: str) -> tuple[float, float, int, float]:
    """Wilcoxon signed-rank test of RAG vs baseline on one metric, paired by question id.
    Returns (statistic, p_value, n, median of rag - baseline); the sign says which side wins."""
    wide = scores.pivot(index="id", columns="system", values=metric).dropna()
    result = wilcoxon(wide["rag"], wide["baseline"])
    return float(result.statistic), float(result.pvalue), len(wide), float((wide["rag"] - wide["baseline"]).median())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="dev", choices=["dev", "test"])
    split = parser.parse_args().split

    scores = pd.read_csv(config.RESULTS_DIR / f"scores_{split}.csv")
    metrics = [c for c in scores.columns if c not in ("id", "type", "system")]

    overall = scores.groupby("system")[metrics].mean()  # pandas means skip NaN
    by_type = scores.groupby(["type", "system"])[SHARED].mean()
    tests = pd.DataFrame([dict(zip(["metric", "statistic", "p_value", "n", "median_diff"], (m, *paired_wilcoxon(scores, m))))
                          for m in SHARED])

    retrieval_file = config.RESULTS_DIR / f"retrieval_{split}.csv"
    retrieval = pd.read_csv(retrieval_file).drop(columns=["id", "type", "rank"]).mean() if retrieval_file.exists() else None

    with pd.option_context("display.width", 200, "display.precision", 3):
        print("== Mean by system ==\n", overall.T, sep="")
        print("\n== Shared metrics by question type ==\n", by_type.unstack("system"), sep="")
        print("\n== Wilcoxon signed-rank, RAG vs baseline ==\n", tests.to_string(index=False), sep="")
        if retrieval is not None:
            print("\n== Retrieval ==\n", retrieval.rename({"rr": "mrr"}).to_string(), sep="")

    summary = overall.T.reset_index(names="metric")
    summary.to_csv(config.RESULTS_DIR / f"summary_{split}.csv", index=False)
    by_type.to_csv(config.RESULTS_DIR / f"summary_by_type_{split}.csv")
    tests.to_csv(config.RESULTS_DIR / f"wilcoxon_{split}.csv", index=False)

    ax = overall[SHARED].T.plot.bar(rot=0, ylim=(0, 1), figsize=(6, 4))
    ax.set_title(f"RAG vs baseline ({split}, n={scores['id'].nunique()})")
    ax.set_ylabel("mean score")
    for bars in ax.containers:
        ax.bar_label(bars, fmt="%.2f")
    plt.tight_layout()
    chart = config.RESULTS_DIR / f"chart_{split}.png"
    plt.savefig(chart, dpi=150)
    print(f"\nsaved summary, wilcoxon and {chart.name} in {config.RESULTS_DIR}")
