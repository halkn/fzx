from pathlib import Path

from fzx.repo import parse_repo_url, repo_list


def test_parse_https_github_url() -> None:
    spec = parse_repo_url("https://github.com/halkn/fzx.git", Path("/home/me/dev"))

    assert spec.clone_url == "https://github.com/halkn/fzx.git"
    assert spec.destination == Path("/home/me/dev/github.com/halkn/fzx")


def test_parse_git_ssh_url() -> None:
    spec = parse_repo_url("git@github.com:halkn/fzx.git", Path("/home/me/dev"))

    assert spec.clone_url == "git@github.com:halkn/fzx.git"
    assert spec.destination == Path("/home/me/dev/github.com/halkn/fzx")


def test_parse_owner_repo_shortcut() -> None:
    spec = parse_repo_url("halkn/fzx.git", Path("/home/me/dev"))

    assert spec.clone_url == "https://github.com/halkn/fzx"
    assert spec.destination == Path("/home/me/dev/github.com/halkn/fzx")


def test_parse_azure_devops_url() -> None:
    spec = parse_repo_url(
        "https://dev.azure.com/acme/widgets/_git/api.git",
        Path("/home/me/dev"),
    )

    assert spec.clone_url == "https://dev.azure.com/acme/widgets/_git/api.git"
    assert spec.destination == Path("/home/me/dev/dev.azure.com/acme/widgets/api")


def test_repo_list_finds_git_directories(tmp_path: Path) -> None:
    (tmp_path / "github.com" / "halkn" / "fzx" / ".git").mkdir(parents=True)
    (tmp_path / "github.com" / "halkn" / "other" / ".git").mkdir(parents=True)
    (tmp_path / "not-a-repo").mkdir()

    assert repo_list(tmp_path) == [
        "github.com/halkn/fzx",
        "github.com/halkn/other",
    ]
