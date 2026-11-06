import shutil
import subprocess
from pathlib import Path

from src import config


def _sha(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


def clone_repo(url: str, ref: str, dest: Path) -> str:
    """Shallow-clone `ref` (tag or branch) into `dest`; return the HEAD commit SHA."""
    if (dest / ".git").exists():
        return _sha(dest)
    result = subprocess.run(["git", "clone", "--depth", "1", "--branch", ref, url, str(dest)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        shutil.rmtree(dest, ignore_errors=True)
        raise RuntimeError(result.stderr.strip())
    return _sha(dest)


if __name__ == "__main__":
    for name, repo in config.REPOS.items():
        print(name, repo["ref"], clone_repo(repo["url"], repo["ref"], repo["dir"]))
