from git_massage import config, git, ai


def test_imports():
    assert config.DEFAULT_CONFIG["model"] == "gpt-4o"
    assert hasattr(git, "get_staged_diff")
    assert hasattr(ai, "generate_message")
