from pathlib import Path

SKIP_DIRS = {"vendor", "third_party", "testdata"}


def _excluded(path: Path) -> bool:
    name = path.name
    return (bool(SKIP_DIRS & set(path.parts))
            or name.endswith(("_test.go", ".pb.go"))
            or name.startswith(("zz_generated", "generated.")))


def list_files(repo_dir: Path, subdirs: list[str], exts: tuple[str, ...]) -> list[Path]:
    """Sorted absolute paths under repo_dir/subdirs with a suffix in exts, minus excluded ones."""
    found = []
    for sub in subdirs:
        for path in (repo_dir / sub).rglob("*"):
            # check the path relative to repo_dir so a "vendor" folder above the repo can't hide everything
            if path.is_file() and path.suffix in exts and not _excluded(path.relative_to(repo_dir)):
                found.append(path)
    return sorted(found)
