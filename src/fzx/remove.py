from __future__ import annotations

import shutil
from pathlib import Path


def split_remove_targets(targets: list[Path]) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    dirs: list[Path] = []
    for target in targets:
        if target.is_dir():
            dirs.append(target)
        else:
            files.append(target)
    dirs.sort(key=lambda path: len(path.parts), reverse=True)
    return files, dirs


def remove_targets(targets: list[Path]) -> None:
    files, dirs = split_remove_targets(targets)
    for file_path in files:
        file_path.unlink(missing_ok=True)
    for dir_path in dirs:
        if dir_path.exists():
            shutil.rmtree(dir_path)
