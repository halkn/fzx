from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from fzx.gitcmd import branch_name_from_line, commit_from_line, worktree_from_line
from fzx.remove import remove_targets
from fzx.repo import parse_repo_url, repo_list
from fzx.tools import (
    command_exists,
    directory_preview_command,
    file_preview_command,
    git_diff_preview_command,
    git_show_preview_command,
    tree_preview_command,
)

FZF_GIT_OPTS = [
    "--height",
    "80%",
    "--layout",
    "reverse",
    "--border",
    "--multi",
    "--bind",
    "ctrl-_:change-preview-window(down,50%|hidden|)",
    "--color",
    "header:italic",
]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        return 1
    except FzxError as exc:
        print(exc, file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fzx")
    subparsers = parser.add_subparsers(required=True)

    history = subparsers.add_parser("history")
    history.set_defaults(func=cmd_history)

    cd = subparsers.add_parser("cd")
    cd.set_defaults(func=cmd_cd)

    rm = subparsers.add_parser("rm")
    rm.set_defaults(func=cmd_rm)

    git = subparsers.add_parser("git")
    git_subparsers = git.add_subparsers(required=True)
    git_branch = git_subparsers.add_parser("branch")
    git_branch.set_defaults(func=cmd_git_branch)
    git_stage = git_subparsers.add_parser("stage")
    git_stage.set_defaults(func=cmd_git_stage)
    git_log = git_subparsers.add_parser("log")
    git_log.set_defaults(func=cmd_git_log)
    git_worktree = git_subparsers.add_parser("worktree")
    git_worktree.set_defaults(func=cmd_git_worktree)

    repo = subparsers.add_parser("repo")
    repo.add_argument("--root", type=Path, default=None)
    repo_subparsers = repo.add_subparsers(required=True)
    repo_list_parser = repo_subparsers.add_parser("list")
    repo_list_parser.set_defaults(func=cmd_repo_list)
    repo_get = repo_subparsers.add_parser("get")
    repo_get.add_argument("url")
    repo_get.set_defaults(func=cmd_repo_get)
    repo_cd = repo_subparsers.add_parser("cd")
    repo_cd.set_defaults(func=cmd_repo_cd)
    return parser


def cmd_history(_args: argparse.Namespace) -> int:
    require_fzf()
    lines = _history_lines()
    selected = run_fzf(lines, ["+s", "--tac"])
    if selected:
        print(_strip_history_number(selected))
    return 0


def cmd_cd(_args: argparse.Namespace) -> int:
    require_fzf()
    if command_exists("fd"):
        result = subprocess.run(
            ["fd", "--type", "d", "--hidden", "--exclude", ".git"],
            check=False,
            capture_output=True,
            text=True,
        )
        candidates = result.stdout.splitlines()
    else:
        result = subprocess.run(
            ["find", ".", "-path", "./.git", "-prune", "-o", "-type", "d", "-print"],
            check=False,
            capture_output=True,
            text=True,
        )
        candidates = [line.removeprefix("./") for line in result.stdout.splitlines() if line != "."]

    selected = run_fzf(
        candidates,
        [
            "--preview",
            directory_preview_command(),
            "--preview-window=right:60%",
            "--bind",
            "ctrl-/:toggle-preview",
        ],
    )
    if selected:
        print(selected)
    return 0


def cmd_rm(_args: argparse.Namespace) -> int:
    require_fzf()
    candidates = _file_candidates()
    selected = run_fzf(
        candidates,
        [
            "--height",
            "80%",
            "--layout",
            "reverse",
            "--border",
            "--multi",
            "--header",
            "TAB: multi-select  ENTER: mark for delete  CTRL-/: toggle preview",
            "--preview",
            file_preview_command(),
            "--preview-window=right:60%",
            "--bind",
            "ctrl-/:toggle-preview",
        ],
    )
    if not selected:
        return 0

    targets = [Path(line) for line in selected.splitlines() if line]
    print("remove targets:")
    for target in targets:
        print(f"  {target}")
    reply = input("delete? [y/N]: ")
    if reply not in {"y", "Y"}:
        return 0
    remove_targets(targets)
    return 0


def cmd_git_branch(_args: argparse.Namespace) -> int:
    require_fzf()
    branches = subprocess.run(
        ["git", "branch", "-a", "--color=always"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    branches = [line for line in branches if "HEAD" not in line]
    selected = run_fzf(
        branches,
        [
            *FZF_GIT_OPTS,
            "--no-multi",
            "--ansi",
            "--header",
            "ENTER: checkout  CTRL-_: toggle preview",
            "--preview",
            (
                'git log --oneline --graph --color=always "$(echo {} '
                '| sed "s/^[* ]*//" '
                '| sed "s/[[:space:]].*//" '
                '| sed "s|remotes/||")" | head -50'
            ),
        ],
    )
    branch = branch_name_from_line(selected)
    if branch:
        return subprocess.run(["git", "switch", branch], check=False).returncode
    return 0


def cmd_git_stage(_args: argparse.Namespace) -> int:
    require_fzf()
    status = _git_status_short()
    run_fzf(
        status,
        [
            *FZF_GIT_OPTS,
            "--ansi",
            "--nth",
            "2..",
            "--header",
            "TAB: multi-select  ENTER: git add  CTRL-U: unstage  CTRL-_: toggle preview",
            "--preview",
            git_diff_preview_command(),
            "--bind",
            (
                "ctrl-u:execute-silent(git restore --staged {2})"
                "+reload(git -c color.status=always status --short)"
            ),
            "--bind",
            "enter:execute-silent(git add {+2})+reload(git -c color.status=always status --short)",
        ],
    )
    return subprocess.run(["git", "status", "--short"], check=False).returncode


def cmd_git_log(_args: argparse.Namespace) -> int:
    require_fzf()
    log = subprocess.run(
        ["git", "log", "--oneline", "--color=always", "--decorate", "--all"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    selected = run_fzf(
        log,
        [
            *FZF_GIT_OPTS,
            "--no-multi",
            "--ansi",
            "--header",
            "ENTER: show stat  CTRL-V: full diff  CTRL-S: stat  CTRL-_: toggle preview",
            "--preview",
            git_show_preview_command(stat=True),
            "--bind",
            f"ctrl-v:change-preview({git_show_preview_command(stat=False)})",
            "--bind",
            f"ctrl-s:change-preview({git_show_preview_command(stat=True)})",
        ],
    )
    commit = commit_from_line(selected)
    if commit:
        return subprocess.run(["git", "show", "--stat", commit], check=False).returncode
    return 0


def cmd_git_worktree(_args: argparse.Namespace) -> int:
    require_fzf()
    worktrees = subprocess.run(
        ["git", "worktree", "list"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    selected = run_fzf(
        worktrees,
        [
            *FZF_GIT_OPTS,
            "--no-multi",
            "--header",
            "ENTER: cd to worktree  CTRL-_: toggle preview",
            "--preview",
            tree_preview_command(),
        ],
    )
    worktree = worktree_from_line(selected)
    if worktree:
        print(worktree)
    return 0


def cmd_repo_list(args: argparse.Namespace) -> int:
    root = _repo_root(args)
    print("\n".join(repo_list(root)))
    return 0


def cmd_repo_get(args: argparse.Namespace) -> int:
    root = _repo_root(args)
    try:
        spec = parse_repo_url(args.url, root)
    except ValueError as exc:
        raise FzxError(f"repo get: cannot parse '{args.url}'") from exc
    if (spec.destination / ".git").is_dir():
        print(f"already exists: {spec.destination}")
        return 0
    spec.destination.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        ["git", "clone", spec.clone_url, str(spec.destination)],
        check=False,
    ).returncode


def cmd_repo_cd(args: argparse.Namespace) -> int:
    require_fzf()
    root = _repo_root(args)
    selected = run_fzf(repo_list(root), [])
    if selected:
        print(root / selected)
    return 0


def run_fzf(candidates: list[str], args: list[str]) -> str:
    input_text = "\n".join(candidates)
    if input_text:
        input_text += "\n"
    result = subprocess.run(
        ["fzf", *args],
        input=input_text,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode in {0, 1, 130}:
        return result.stdout.rstrip("\n")
    raise FzxError(result.stderr.strip() or f"fzf failed with exit code {result.returncode}")


def require_fzf() -> None:
    if not command_exists("fzf"):
        raise FzxError("fzx: fzf is not installed or not in PATH")


def _repo_root(args: argparse.Namespace) -> Path:
    value = args.root or os.environ.get("FZX_REPO_ROOT") or "~/dev"
    return Path(value).expanduser()


def _file_candidates() -> list[str]:
    if command_exists("fd"):
        result = subprocess.run(
            ["fd", "--hidden", "--strip-cwd-prefix", "--exclude", ".git"],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout.splitlines()
    result = subprocess.run(
        ["find", ".", "-path", "./.git", "-prune", "-o", "-mindepth", "1", "-print"],
        check=False,
        capture_output=True,
        text=True,
    )
    return [line.removeprefix("./") for line in result.stdout.splitlines()]


def _git_status_short() -> list[str]:
    return subprocess.run(
        ["git", "-c", "color.status=always", "status", "--short"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout.splitlines()


def _history_lines() -> list[str]:
    if not sys.stdin.isatty():
        return sys.stdin.read().splitlines()
    histfile = os.environ.get("HISTFILE")
    if not histfile:
        return []
    path = Path(histfile).expanduser()
    if not path.exists():
        return []
    return path.read_text(errors="replace").splitlines()


def _strip_history_number(line: str) -> str:
    stripped = line.lstrip()
    parts = stripped.split(maxsplit=1)
    if len(parts) == 2 and parts[0].rstrip("*").isdigit():
        return parts[1].replace("\\", "\\\\")
    if stripped.startswith(": "):
        _, _, command = stripped.partition(";")
        return command.replace("\\", "\\\\")
    return line.replace("\\", "\\\\")


class FzxError(Exception):
    pass
