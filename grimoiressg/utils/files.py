from collections.abc import Callable
import glob
import os
from typing import Any


def to_relative(path: str):
    trimmed = path.removeprefix(os.getcwd())
    if trimmed != path:
        trimmed = "." + trimmed
    return trimmed


def for_each_glob(glob_path: str, callback: Callable[[str], list[dict[str, Any]]]):
    results = []

    for filename in glob.glob(os.path.realpath(glob_path)):
        results.extend(callback(filename))

    return results
