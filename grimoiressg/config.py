import logging

import yaml
from yaml import Loader

from grimoiressg.context import Context
from grimoiressg.modules import available_modules, load_external_module
from grimoiressg.utils import logger


def default_config() -> dict[str, list[str]]:
    return {
        "enabled_modules": [
            "tags",
            "markdown",
            "templating",
        ],
    }


def read_config(context: Context):
    config_file = context.config_file

    if not config_file:
        logger.info("No config file given; using default config")

        config = default_config()

    else:
        logger.info("Loading config file...")

        with open(config_file, "r") as file:
            config = yaml.load(file, Loader) or {}

    for module in config.get("load_modules", []):
        logger.debug(" Loading external module %s", module)

        load_external_module(module)

    logger.debug("Enabled modules:")

    for module in config.get("enabled_modules", []):
        logger.debug(" - %s", module)

        if module not in available_modules:
            logger.critical("Module does not exist: %s", module)
            logging.shutdown()
            exit(1)

    return config
