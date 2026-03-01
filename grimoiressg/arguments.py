import argparse

from grimoiressg.context import Context
from grimoiressg.utils import logger


def parse_arguments_to_initial_context() -> Context:
    parser = argparse.ArgumentParser(
        description="""
            Grimoire is a minimalistic Static Site Generator.
            In the simplest case the only argument needed is at least one content file. \
            The rest of the flags is used to customize the behavior.
        """
    )
    _ = parser.add_argument("content_file", nargs="+", help="one or more content files")
    _ = parser.add_argument(
        "-o",
        "--output",
        default="./output/",
        help="the output directory (default: ./output/)",
    )
    _ = parser.add_argument(
        "-c", "--config", help="the config file to use", default=None
    )

    args, _ = parser.parse_known_args()

    context = Context(
        output_dir=args.output,
        config_file=args.config,
        filenames=args.content_file,
    )

    logger.debug("Output directory: %s", context.output_dir)
    logger.debug("Config file: %s", context.config_file)
    logger.debug("Content files:")

    for filename in context.filenames:
        logger.debug(" - %s", filename)

    return context
