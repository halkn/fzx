from __future__ import annotations

import shutil
from collections.abc import Callable

ToolExists = Callable[[str], bool]


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def directory_preview_command(exists: ToolExists = command_exists) -> str:
    if exists("lsd"):
        return "lsd -lah {} && echo && lsd --tree --depth 2 {}"
    return "ls -lah {}"


def file_preview_command(exists: ToolExists = command_exists) -> str:
    if exists("bat") and exists("lsd"):
        return (
            "if test -d {}; then lsd -lah {} && echo && lsd --tree --depth 2 {}; "
            "else bat --style=plain --color=always --line-range=:200 {}; fi"
        )
    if exists("bat"):
        return (
            "if test -d {}; then ls -lah {}; "
            "else bat --style=plain --color=always --line-range=:200 {}; fi"
        )
    if exists("lsd"):
        return (
            "if test -d {}; then lsd -lah {} && echo && lsd --tree --depth 2 {}; "
            'else sed -n "1,200p" {}; fi'
        )
    return 'if test -d {}; then ls -lah {}; else sed -n "1,200p" {}; fi'


def git_diff_preview_command(exists: ToolExists = command_exists) -> str:
    base = "git diff --color=always -- {2}"
    if exists("delta"):
        return f'{base} | delta --paging=never --width "${{FZF_PREVIEW_COLUMNS:-${{COLUMNS:-80}}}}"'
    return base


def git_show_preview_command(exists: ToolExists = command_exists, *, stat: bool) -> str:
    show = "git show --color=always"
    if stat:
        show = f"{show} --stat"
    show = f"{show} {{1}}"
    if exists("delta"):
        return f'{show} | delta --paging=never --width "${{FZF_PREVIEW_COLUMNS:-${{COLUMNS:-80}}}}"'
    return show


def tree_preview_command(exists: ToolExists = command_exists) -> str:
    if exists("eza"):
        return "eza --tree --color=always --level 2 {1}"
    if exists("lsd"):
        return "lsd --tree --depth 2 {1}"
    return "find {1} -maxdepth 2 -print"
