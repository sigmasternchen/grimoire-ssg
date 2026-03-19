from collections.abc import Callable
import glob
import os
from time import sleep, time
from typing import Any
from pathlib import Path


def to_relative(path: str):
    trimmed = path.removeprefix(os.getcwd())
    if trimmed != path:
        trimmed = "." + trimmed
    return trimmed


def for_each_glob(glob_path: Path, callback: Callable[[Path], list[dict[str, Any]]]):
    results = []

    if "*" not in glob_path.as_posix():
        return callback(Path(glob_path))

    if glob_path.is_absolute():
        glob_path = glob_path.relative_to("/")

    for filename in glob_path.parent.glob(glob_path.name):
        results.extend(callback(filename))

    return results
