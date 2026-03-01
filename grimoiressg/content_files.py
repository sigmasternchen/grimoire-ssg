import os
import pathlib
from typing import Any

import yaml
from yaml import Loader

from grimoiressg.context import Context
from grimoiressg.utils import logger, for_each_glob, to_relative

possible_separators = (
    "---\n",
    "+++\n",
)


def handle_file(filename: str) -> list[dict[str, Any]]:
    logger.debug(" Reading %s...", to_relative(filename))

    match pathlib.Path(filename).suffix:
        case ".yml" | ".yaml":
            data = handle_yaml(filename)
        case ".md":
            data = handle_markdown(filename)
        case _:
            raise ValueError(filename)

    data["filename"] = filename
    data["relative_filename"] = to_relative(filename)

    results = [data]

    relative_dir = os.path.dirname(filename)
    for filename in data.get("include", []):
        filename = relative_dir + "/" + filename
        sub_data = for_each_glob(filename, handle_file)
        results.extend(sub_data)

    return results


def handle_markdown(filename: str) -> dict[str, Any]:
    data = {}

    with open(filename, "r") as file:
        _frontmatter = ""
        content = ""

        if content := file.read():
            _frontmatter, content = split_frontmatter(content)

        if _frontmatter:
            data: dict[str, Any] = yaml.safe_load(_frontmatter)

        if content != "":
            data["markdown"] = content

    return data


def handle_yaml(filename: str) -> dict[str, Any]:
    with open(filename, "r") as file:
        return yaml.load(file, Loader)


def expect_separator(input: str) -> str | None:
    separator_candidate = input[0:4]
    if separator_candidate in possible_separators:
        return separator_candidate

    return None


def split_frontmatter(input: str) -> tuple[str | None, str]:
    separator = expect_separator(input)
    if not separator:
        return None, input

    frontmatter_end = input.find(separator, 4)
    if frontmatter_end == -1:
        # frontmatter never ends -> there is no front matter
        return None, input

    return input[4:frontmatter_end], input[frontmatter_end + 4 :]


def deduplicate(candidates: list[Any]):
    names = set()
    results = []

    for candidate in candidates:
        if candidate["relative_filename"] not in names:
            names.add(candidate["relative_filename"])
            results.append(candidate)

    return results


def recursively_read_files(context: Context):
    data: list[dict[str, Any]] = []

    logger.info("Reading content files...")

    for filename in context.filenames:
        data.extend(for_each_glob(filename, handle_file))

    data = deduplicate(data)

    logger.info(f"Read %d files in total.", len(data))

    return data
