from __future__ import annotations


def branch_name_from_line(line: str) -> str:
    line = line.strip()
    line = line.removeprefix("*").strip()
    name = line.split(maxsplit=1)[0]
    return name.removeprefix("remotes/")


def path_from_status_line(line: str) -> str:
    parts = line.split(maxsplit=1)
    if len(parts) < 2:
        return ""
    return parts[1]


def commit_from_line(line: str) -> str:
    return line.split(maxsplit=1)[0] if line.strip() else ""


def worktree_from_line(line: str) -> str:
    return line.split(maxsplit=1)[0] if line.strip() else ""
