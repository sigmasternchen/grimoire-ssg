import logging
from typing import Any

from grimoiressg.arguments import parse_arguments_to_initial_context
from grimoiressg.config import read_config
from grimoiressg.content_files import recursively_read_files
from grimoiressg.context import Context
from grimoiressg.modules import available_modules
from grimoiressg.utils import logger


def apply_modules(data: Any, config: dict[str, Any], context: Context):
    for module in config.get("enabled_modules", []):
        logger.info("Applying module %s...", module)

        available_modules[module](data, context, config)


def main():
    context = parse_arguments_to_initial_context()
    config = read_config(context)

    data = recursively_read_files(context)
    apply_modules(data, config, context)

    logger.info("Done.")
    logging.shutdown()
