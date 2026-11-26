"""Make the report figures. Run: uv run python docs/figures/make_figures.py

Every figure is 6 in wide so it fits A4 with 1-inch margins (6.27 in text width).
"""
import json
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RESULTS = ROOT / "eval" / "results"

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
                     "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 300, "savefig.bbox": "tight"})
BLUE, ORANGE, GREEN, GREY = "#2b6cb0", "#dd6b20", "#2f855a", "#718096"
AREAS = {"pkg/scheduler": "scheduler", "pkg/kubelet": "kubelet",
         "staging/src/k8s.io/client-go": "client-go", "contributors/": "docs"}


def area(path: str) -> str:
    return next((name for prefix, name in AREAS.items() if path.startswith(prefix)), "other")


def save(fig, name):
    fig.savefig(OUT / name)
    plt.close(fig)
    print("wrote", name)


def architecture():
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.4)
    ax.axis("off")

    def box(x, y, text, color, w=2.4, h=1.05):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", fc=color, ec="black", lw=0.6, alpha=0.9))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="->", lw=0.9))

    ax.text(0.1, 7.1, "Offline indexing", fontsize=10, weight="bold")
    row = 5.8
    for i, t in enumerate(["Clone repos\n(pinned commits)", "Filter files\n(skip vendor, tests,\ngenerated)",
                           "Chunk\nGo: per function\nDocs: by heading", "Embed\nbge-small-en-v1.5\n→ Chroma DB"]):
        box(0.1 + i * 3, row, t, "#e6f0fa")
        if i:
            arrow(0.1 + i * 3 - 0.55, row + 0.47, 0.1 + i * 3, row + 0.47)

    ax.text(0.1, 4.9, "Answering a question", fontsize=10, weight="bold")
    row = 3.6
    box(0.1, row, "User question\n(CLI or Streamlit)", "#fdf2e6")
    box(3.1, row, "Retrieve top-8\nchunks (cosine)", "#e6f0fa")
    box(6.1, row, "RAG prompt\n(chunks + rules)", "#e6f0fa")
    box(9.1, row, "qwen2.5-coder:7b\n→ answer +\nGitHub links", "#e8f5ec")
    arrow(2.55, row + 0.47, 3.1, row + 0.47)
    arrow(5.55, row + 0.47, 6.1, row + 0.47)
    arrow(8.55, row + 0.47, 9.1, row + 0.47)
    arrow(10.3, 5.8, 4.3, row + 0.95)  # Chroma -> retrieve
    box(3.1, 2.1, "Baseline: same LLM,\nno context", "#f0f0f0", w=2.9)
    arrow(1.3, row, 3.1, 2.55)

    ax.text(0.1, 1.45, "Evaluation", fontsize=10, weight="bold")
    box(0.1, 0.1, "52 questions\n(42 dev / 10 test)", "#fdf2e6")
    box(3.1, 0.1, "hit@k, MRR\n(retrieval)", "#f5e6fa")
    box(6.1, 0.1, "RAGAS judge\nllama3.1:8b", "#f5e6fa")
    box(9.1, 0.1, "Wilcoxon test\n+ charts", "#f5e6fa")
    arrow(2.55, 0.57, 3.1, 0.57)
    arrow(5.55, 0.57, 6.1, 0.57)
    arrow(8.55, 0.57, 9.1, 0.57)
    save(fig, "fig5_architecture.png")


def corpus_figures(chunks: pd.DataFrame):
    # Fig 2: chunks and files per area
    order = ["client-go", "kubelet", "scheduler", "docs"]
    counts = chunks.groupby("area").agg(chunks=("id", "size"), files=("path", "nunique")).loc[order]
    fig, axes = plt.subplots(1, 2, figsize=(6, 2.4))
    for ax, col, color in zip(axes, ["files", "chunks"], [GREY, BLUE]):
        bars = ax.barh(order[::-1], counts[col][::-1], color=color)
        ax.bar_label(bars, fmt="{:,.0f}", padding=2, fontsize=8)
        ax.set_title(f"Number of {col}")
        ax.set_xlim(0, counts[col].max() * 1.25)
    fig.tight_layout()
    save(fig, "fig1_corpus_by_area.png")

    # Fig 3: chunk length histogram, code vs docs (log x)
    fig, ax = plt.subplots(figsize=(6, 2.6))
    bins = [10 * 1.25 ** i for i in range(33)]
    for kind, color, label in [("code", BLUE, "Go code"), ("doc", ORANGE, "Markdown docs")]:
        ax.hist(chunks.loc[chunks.kind == kind, "chars"], bins=bins, alpha=0.7, color=color, label=label)
    ax.set_xscale("log")
    ax.axvline(chunks.chars.median(), color="black", ls="--", lw=0.8)
    ax.text(chunks.chars.median() * 1.1, ax.get_ylim()[1] * 0.9, f"median = {chunks.chars.median():.0f}", fontsize=8)
    ax.set_xlabel("Chunk length (characters, log scale)")
    ax.set_ylabel("Number of chunks")
    ax.legend(frameon=False)
    save(fig, "fig2_chunk_length_hist.png")

    # Fig 4: box plot of chunk length per area
    fig, ax = plt.subplots(figsize=(6, 2.4))
    ax.boxplot([chunks.loc[chunks.area == a, "chars"] for a in order], tick_labels=order, orientation="horizontal",
               flierprops=dict(markersize=2, alpha=0.3), medianprops=dict(color=ORANGE))
    ax.set_xscale("log")
    ax.set_xlabel("Chunk length (characters, log scale)")
    ax.invert_yaxis()
    save(fig, "fig3_chunk_length_box.png")


def question_figure(questions: pd.DataFrame):
    names = {"sched": "scheduler", "kubelet": "kubelet", "cgo": "client-go", "docs": "docs"}
    questions["area"] = questions["id"].str.split("-").str[0].map(names)
    table = pd.crosstab(questions["area"], questions["type"]).loc[list(names.values())]
    table = table[["where", "how", "interaction", "docs"]]
    fig, ax = plt.subplots(figsize=(6, 2.4))
    table.plot.barh(stacked=True, ax=ax, color=[BLUE, GREEN, ORANGE, GREY], width=0.6)
    ax.invert_yaxis()
    ax.set_xlabel("Number of questions")
    ax.set_ylabel("")
    ax.legend(title="Question type", frameon=False, bbox_to_anchor=(1.0, 1.0), loc="upper left")
    save(fig, "fig4_questions_by_area_type.png")


def retrieval_figure():
    df = pd.read_csv(RESULTS / "retrieval_dev.csv")
    ks = [4, 8, 16]
    fig, ax = plt.subplots(figsize=(6, 2.6))
    for t, color in zip(["docs", "where", "how", "interaction"], [GREY, BLUE, GREEN, ORANGE]):
        sub = df[df.type == t]
        ax.plot(ks, [sub[f"hit@{k}"].mean() for k in ks], marker="o", color=color, label=f"{t} (n={len(sub)})")
    ax.plot(ks, [df[f"hit@{k}"].mean() for k in ks], marker="s", color="black", lw=2, label=f"overall (n={len(df)})")
    ax.set_xticks(ks)
    ax.set_xlabel("k (number of retrieved chunks)")
    ax.set_ylabel("hit@k")
    ax.set_ylim(0.6, 1.03)
    ax.legend(frameon=False, fontsize=8, bbox_to_anchor=(1.0, 1.0), loc="upper left")
    save(fig, "fig6_retrieval_hit_at_k.png")


def answer_figure():
    overall = pd.read_csv(RESULTS / "summary_dev.csv").set_index("metric")
    by_type = pd.read_csv(RESULTS / "summary_by_type_dev.csv")
    fig, axes = plt.subplots(1, 2, figsize=(6, 2.8), gridspec_kw={"width_ratios": [1.1, 1]})

    labels = {"answer_correctness": "Correctness", "answer_relevancy": "Relevancy", "faithfulness": "Faithful.",
              "llm_context_precision_with_reference": "Ctx precision", "context_recall": "Ctx recall"}
    x = range(len(labels))
    ax = axes[0]
    b = ax.bar([i - 0.2 for i in x], overall.loc[list(labels), "baseline"].fillna(0), 0.4, color=GREY, label="Baseline")
    r = ax.bar([i + 0.2 for i in x], overall.loc[list(labels), "rag"], 0.4, color=BLUE, label="RAG")
    ax.bar_label(b, labels=[f"{v:.2f}" if v else "" for v in overall.loc[list(labels), "baseline"].fillna(0)], fontsize=6.5)
    ax.bar_label(r, fmt="%.2f", fontsize=6.5)
    ax.set_xticks(list(x), labels.values(), rotation=30, ha="right", fontsize=8)
    ax.set_ylim(0, 1.25)
    ax.set_title("(a) Mean RAGAS scores", fontsize=9.5)
    ax.legend(frameon=False, fontsize=8, loc="upper center", ncol=2)

    ax = axes[1]
    wide = by_type.pivot(index="type", columns="system", values="answer_correctness").loc[["where", "how", "interaction", "docs"]]
    xs = range(len(wide))
    b = ax.bar([i - 0.2 for i in xs], wide["baseline"], 0.4, color=GREY)
    r = ax.bar([i + 0.2 for i in xs], wide["rag"], 0.4, color=BLUE)
    ax.bar_label(b, fmt="%.2f", fontsize=6.5)
    ax.bar_label(r, fmt="%.2f", fontsize=6.5)
    ax.set_xticks(list(xs), wide.index, fontsize=8)
    ax.set_ylim(0, 0.8)
    ax.set_title("(b) Correctness by question type", fontsize=9.5)
    fig.tight_layout()
    save(fig, "fig7_rag_vs_baseline.png")


if __name__ == "__main__":
    rows = [json.loads(line) for line in (ROOT / "data" / "chunks.jsonl").open()]
    chunks = pd.DataFrame(rows)
    chunks["area"] = chunks["path"].map(area)
    chunks["chars"] = chunks["text"].str.len()
    questions = pd.DataFrame([json.loads(line) for line in (ROOT / "eval" / "questions.jsonl").open() if line.strip()])

    architecture()
    corpus_figures(chunks)
    question_figure(questions)
    retrieval_figure()
    answer_figure()
