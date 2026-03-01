import os

from grimoiressg.context import Context
from jinja2 import Environment, FileSystemLoader

from grimoiressg.utils import to_relative, logger

from dataclasses import asdict

jinja_env = Environment(loader=FileSystemLoader("/"))


def render_templates(data, context: Context, _config):
    files_written = 0
    # render templates in reverse order, so included renderings can be used

    for entry in reversed(data):
        if "template" in entry:
            template_path = os.path.realpath(
                os.path.dirname(entry["filename"]) + "/" + entry["template"]
            )

            template_dir = os.path.dirname(template_path)
            logger.debug("Rendering template for %s...", entry["relative_filename"])

            template = jinja_env.get_template(template_path)
            entry["rendered"] = template.render(
                **asdict(context), current=entry, all=data, template_dir=template_dir
            )

        if "rendered" in entry and "output" in entry:
            files_written += 1
            filename = os.path.realpath(context.output_dir + "/" + entry["output"])

            logger.debug(" writing to %s", to_relative(filename))
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, "w") as file:
                file.write(entry["rendered"])

    logger.debug("%d rendered", files_written)
