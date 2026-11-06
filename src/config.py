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
