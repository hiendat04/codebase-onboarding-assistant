from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CHROMA_DIR = ROOT / "chroma_db"

# ref is a git tag or branch; SHAs are what we actually indexed (used for GitHub permalinks)
K8S_SHA = "c50e5395f1ae2d4a2c05f28fdcc38c0916cc1a32"
COMMUNITY_SHA = "307ae50e8e4246de172f195c73e3f026b4f0c7ff"

REPOS = {
    "kubernetes": {
        "url": "https://github.com/kubernetes/kubernetes.git",
        "ref": "v1.37.2",
        "dir": DATA_DIR / "kubernetes",
    },
    "community": {
        "url": "https://github.com/kubernetes/community.git",
        "ref": "main",
        "dir": DATA_DIR / "community",
    },
}

# starting scope, grow later
SUBSYSTEMS = ["pkg/scheduler", "pkg/kubelet", "staging/src/k8s.io/client-go"]

TOP_K = 8

MAX_CHARS = 6000  # about 1,500 tokens
OVERLAP_LINES = 5
DOC_DIRS = ["contributors/devel", "contributors/guide"]  # in the community repo
CHUNKS_FILE = DATA_DIR / "chunks.jsonl"

# indexing (Phase 2)
EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # 384 dims; reads at most 512 tokens per chunk
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # bge wants this on questions only
COLLECTION = "k8s"
