from decimal import Context
import markdown

from grimoiressg.utils import logger


def compile_markdown(data, _context: Context, _config):
    for entry in data:
        if "markdown" in entry:
            logger.debug("Compiling markdown for %s...", entry["relative_filename"])
            entry["markdown_compiled"] = markdown.markdown(
                entry["markdown"], extensions=["tables"]
            )
