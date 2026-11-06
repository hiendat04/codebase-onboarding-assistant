import subprocess

import pytest

from src.clone import clone_repo


@pytest.fixture
def origin(tmp_path):
    path = tmp_path / "origin"
    path.mkdir()
    run = lambda *a: subprocess.run(["git", "-C", str(path), *a], check=True, capture_output=True)
    run("init", "-q", "-b", "main")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x")
    run("tag", "v1.0.0")
    return path


def test_clone_returns_sha_and_is_idempotent(origin, tmp_path):
    dest = tmp_path / "out"
    sha = clone_repo(f"file://{origin}", "v1.0.0", dest)
    assert len(sha) == 40
    assert clone_repo(f"file://{origin}", "v1.0.0", dest) == sha  # second call: no re-clone


def test_bad_ref_raises_and_leaves_nothing(origin, tmp_path):
    dest = tmp_path / "out"
    with pytest.raises(RuntimeError):
        clone_repo(f"file://{origin}", "v9.9.9", dest)
    assert not dest.exists()
