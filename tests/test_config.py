from src import config


def test_repos_defined():
    assert set(config.REPOS) == {"kubernetes", "community"}
    for repo in config.REPOS.values():
        assert repo["url"].startswith("https://github.com/kubernetes/")
        assert repo["ref"]
        assert repo["dir"].parent == config.DATA_DIR


def test_scope_and_defaults():
    assert "pkg/scheduler" in config.SUBSYSTEMS
    assert config.TOP_K == 8
