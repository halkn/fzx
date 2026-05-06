from fzx.cli import main


def test_repo_get_parse_error_is_reported_without_traceback(capsys) -> None:
    assert main(["repo", "get", "invalid"]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "repo get: cannot parse 'invalid'\n"
