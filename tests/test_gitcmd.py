from fzx.gitcmd import (
    branch_name_from_line,
    commit_from_line,
    path_from_status_line,
    worktree_from_line,
)


def test_branch_name_from_line_removes_current_marker_and_remote_prefix() -> None:
    assert branch_name_from_line("* main") == "main"
    assert branch_name_from_line("  remotes/origin/topic 123") == "origin/topic"


def test_path_from_status_line_uses_second_field() -> None:
    assert path_from_status_line(" M src/fzx/cli.py") == "src/fzx/cli.py"
    assert path_from_status_line("?? README.md") == "README.md"


def test_commit_and_worktree_extractors() -> None:
    assert commit_from_line("abc1234 message") == "abc1234"
    assert worktree_from_line("/tmp/repo abc123 [main]") == "/tmp/repo"
