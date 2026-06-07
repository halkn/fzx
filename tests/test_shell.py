import pytest

from fzx.cli import main
from fzx.shell import SUPPORTED_SHELLS, init_script


def test_zsh_is_supported() -> None:
    assert "zsh" in SUPPORTED_SHELLS


def test_init_script_defines_widgets_and_default_bindings() -> None:
    script = init_script("zsh")
    bindings = {
        "fzx-history-widget": "${FZX_HISTORY_KEY:-^R}",
        "fzx-cd-widget": "${FZX_CD_KEY:-^[c}",
        "fzx-git-worktree-widget": "${FZX_GIT_WORKTREE_KEY:-^[w}",
        "fzx-repo-cd-widget": "${FZX_REPO_CD_KEY:-^[r}",
    }
    for widget, key in bindings.items():
        assert f"zle -N {widget}" in script
        assert f'bindkey "{key}" {widget}' in script
    assert "FZX_NO_DEFAULT_KEYBINDINGS" in script


def test_init_script_rejects_unknown_shell() -> None:
    with pytest.raises(ValueError, match="unsupported shell 'fish'"):
        init_script("fish")


def test_cmd_init_prints_script(capsys) -> None:
    assert main(["init", "zsh"]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert "fzx-history-widget" in captured.out
    assert captured.out == init_script("zsh")


def test_cmd_init_rejects_unknown_shell_via_argparse(capsys) -> None:
    with pytest.raises(SystemExit):
        main(["init", "fish"])

    captured = capsys.readouterr()
    assert "invalid choice" in captured.err
