from fzx.tools import (
    directory_preview_command,
    file_preview_command,
    git_diff_preview_command,
    git_show_preview_command,
    tree_preview_command,
)


def test_directory_preview_prefers_lsd() -> None:
    assert directory_preview_command(lambda name: name == "lsd") == (
        "lsd -lah {} && echo && lsd --tree --depth 2 {}"
    )


def test_directory_preview_falls_back_to_ls() -> None:
    assert directory_preview_command(lambda _name: False) == "ls -lah {}"


def test_file_preview_uses_posix_shell_and_fallbacks() -> None:
    assert file_preview_command(lambda _name: False) == (
        'if test -d {}; then ls -lah {}; else sed -n "1,200p" {}; fi'
    )


def test_git_preview_falls_back_without_delta() -> None:
    assert git_diff_preview_command(lambda _name: False) == "git diff --color=always -- {2}"
    assert git_show_preview_command(lambda _name: False, stat=True) == (
        "git show --color=always --stat {1}"
    )


def test_worktree_preview_prefers_available_tree_tool() -> None:
    assert tree_preview_command(lambda name: name == "eza") == (
        "eza --tree --color=always --level 2 {1}"
    )
    assert tree_preview_command(lambda name: name == "lsd") == "lsd --tree --depth 2 {1}"
    assert tree_preview_command(lambda _name: False) == "find {1} -maxdepth 2 -print"
