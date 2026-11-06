from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CHROMA_DIR = ROOT / "chroma_db"

# ref is a git tag or branch; commit SHAs are added after the first clone
REPOS = {
    "kubernetes": {
        "url": "https://github.com/kubernetes/kubernetes.git",
        "ref": "v1.37.2",
        "dir": DATA_DIR / "kubernetes",
    },
    "community": {
        "url": "https://github.com/kubernetes/community.git",
        "ref": "master",
        "dir": DATA_DIR / "community",
    },
}

# starting scope, grow later
SUBSYSTEMS = ["pkg/scheduler", "pkg/kubelet", "staging/src/k8s.io/client-go"]

TOP_K = 8
