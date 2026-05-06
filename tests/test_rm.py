from pathlib import Path

from fzx.remove import split_remove_targets


def test_split_remove_targets_files_first_and_deep_directories_first(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    nested = tmp_path / "a" / "b"
    parent = tmp_path / "a"
    file_path.write_text("x")
    nested.mkdir(parents=True)

    files, dirs = split_remove_targets([parent, file_path, nested])

    assert files == [file_path]
    assert dirs == [nested, parent]
