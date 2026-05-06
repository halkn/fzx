from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class RepoSpec:
    clone_url: str
    destination: Path


def parse_repo_url(value: str, root: Path) -> RepoSpec:
    if "dev.azure.com" in value:
        return _parse_azure_url(value, root)
    if value.startswith("https://"):
        return _parse_https_url(value, root)
    if value.startswith("git@"):
        return _parse_git_ssh_url(value, root)
    if "/" in value:
        owner, name = value.split("/", 1)
        if not owner or not name or "/" in name:
            raise ValueError(f"cannot parse repo url: {value}")
        name = _strip_git_suffix(name)
        return RepoSpec(
            clone_url=f"https://github.com/{owner}/{name}",
            destination=root / "github.com" / owner / name,
        )
    raise ValueError(f"cannot parse repo url: {value}")


def repo_list(root: Path) -> list[str]:
    if not root.exists():
        return []

    repos = []
    for git_dir in root.glob("*/*/*/.git"):
        if git_dir.is_dir():
            repos.append(git_dir.parent.relative_to(root).as_posix())
    for git_dir in root.glob("*/*/*/*/.git"):
        if git_dir.is_dir():
            repos.append(git_dir.parent.relative_to(root).as_posix())
    return sorted(set(repos))


def _parse_https_url(value: str, root: Path) -> RepoSpec:
    parsed = urlparse(value)
    parts = [part for part in parsed.path.split("/") if part]
    if not parsed.netloc or len(parts) < 2:
        raise ValueError(f"cannot parse repo url: {value}")
    owner = parts[0]
    name = _strip_git_suffix(parts[1])
    return RepoSpec(clone_url=value, destination=root / parsed.netloc / owner / name)


def _parse_git_ssh_url(value: str, root: Path) -> RepoSpec:
    stripped = value.removeprefix("git@")
    host, sep, path = stripped.partition(":")
    if not host or sep != ":":
        raise ValueError(f"cannot parse repo url: {value}")
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        raise ValueError(f"cannot parse repo url: {value}")
    owner = parts[0]
    name = _strip_git_suffix(parts[1])
    return RepoSpec(clone_url=value, destination=root / host / owner / name)


def _parse_azure_url(value: str, root: Path) -> RepoSpec:
    marker = "dev.azure.com/"
    if marker not in value:
        raise ValueError(f"cannot parse repo url: {value}")
    repo_path = value.split(marker, 1)[1]
    repo_path = repo_path.removeprefix("@dev.azure.com/")
    parts = [part for part in repo_path.split("/") if part]
    if len(parts) < 4 or parts[2] != "_git":
        raise ValueError(f"cannot parse repo url: {value}")
    org, project, _, name = parts[:4]
    return RepoSpec(
        clone_url=value,
        destination=root / "dev.azure.com" / org / project / _strip_git_suffix(name),
    )


def _strip_git_suffix(value: str) -> str:
    return value.removesuffix(".git")
