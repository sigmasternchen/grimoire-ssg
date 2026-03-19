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


def handle_file(filename: pathlib.Path) -> list[dict[str, Any]]:
    logger.debug(" Reading %s...", filename.name)

    file_suffix = pathlib.Path(filename).suffix
    match file_suffix:
        case ".yml" | ".yaml":
            data = handle_yaml(filename)
        case ".md":
            data = handle_markdown(filename)
        case _:
            raise ValueError(f"File extension {file_suffix} not supported.")

    data["filename"] = filename
    data["relative_filename"] = filename.name

    results = [data]

    relative_dir = filename.parent
    for filename in data.get("include", []):
        filename = relative_dir / filename

        sub_data = for_each_glob(filename, handle_file)

        results.extend(sub_data)

    return results


def handle_markdown(filename: str) -> dict[str, Any]:
    parsed_data: dict[str, Any] = {}

    with open(filename, "r") as file:
        meta_data = ""
        content = ""

        if content := file.read():
            meta_data, content = split_frontmatter(content)

        if meta_data:
            parsed_data = yaml.safe_load(meta_data)

        if content != "":
            parsed_data["markdown"] = content

    return parsed_data


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
        filename = pathlib.Path(filename)
        data.extend(for_each_glob(filename, handle_file))

    data = deduplicate(data)

    logger.info(f"Read {len(data)} files in total.")

    return data
