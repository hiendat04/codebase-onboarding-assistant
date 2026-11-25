import math

import pandas as pd

from src.evaluation.report import paired_wilcoxon


def test_paired_wilcoxon_drops_nan_pairs():
    ids = [f"q{i}" for i in range(8)]
    rag = [0.9, 0.8, 0.85, 0.7, 0.95, 0.75, 0.9, 0.8]
    base = [0.1, 0.2, 0.3, 0.15, 0.25, 0.05, 0.35, math.nan]
    df = pd.DataFrame({"id": ids * 2, "system": ["rag"] * 8 + ["baseline"] * 8,
                       "answer_correctness": rag + base})
    stat, p, n, diff = paired_wilcoxon(df, "answer_correctness")
    assert n == 7
    assert p < 0.05
    assert diff > 0
