from src.files import list_files


def test_list_files_applies_excludes(tmp_path):
    for name in ["a.go", "a_test.go", "x.pb.go", "zz_generated.deepcopy.go", "generated.go",
                 "vendor/v.go", "testdata/t.go", "applyconfigurations/c.go", "sub/b.go", "README.md"]:
        f = tmp_path / "pkg" / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x")

    assert list_files(tmp_path, ["pkg", "nope"], (".go",)) == [
        tmp_path / "pkg" / "a.go",
        tmp_path / "pkg" / "sub" / "b.go",
    ]
    assert list_files(tmp_path, ["pkg"], (".md",)) == [tmp_path / "pkg" / "README.md"]
