import gzip
import os
from itertools import batched
from xml.etree import ElementTree as ET

from grimoiressg.context import Context
from grimoiressg.utils import to_relative, logger

INDEX_FILE_STRATEGY_NONE = "none"
INDEX_FILE_STRATEGY_AUTO = "auto"


def sitemaps_default_config():
    return {
        "file_prefix": "sitemap",
        "loc_prefix": "https://example.com/",
        "index_file_strategy": INDEX_FILE_STRATEGY_AUTO,
        "compression": False,
    }


def get_files_to_map(data, sitemap_config):
    content_for_sitemap = filter(
        lambda item: item.get("output", False) and not item.get("skip_sitemap", False),
        data,
    )

    if sitemap_config["index_file_strategy"] == INDEX_FILE_STRATEGY_AUTO:
        # maximum number of entries is 50 000, however there is also a 50 MiB size limit
        # -> make 20 000 item batches - to be safe
        return list(batched(content_for_sitemap, 20000))
    else:
        return [content_for_sitemap]


def get_sitemap_file_suffix(sitemap_config):
    if sitemap_config["compression"]:
        return ".xml.gz"
    else:
        return ".xml"


def save_sitemaps_file(xml_data, name, context: Context, sitemap_config):
    xml_str = ET.tostring(xml_data, encoding="utf8")

    filename = os.path.realpath(
        context.output_dir + "/" + name + get_sitemap_file_suffix(sitemap_config)
    )
    logger.debug("Writing sitemap %s", to_relative(filename))

    open_function = gzip.open if sitemap_config["compression"] else open
    with open_function(filename, "wb") as file:
        file.write(xml_str)


def generate_index_file(context, sitemap_config, number_of_batches):
    root = ET.Element(
        "sitemapindex",
        attrib={
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.sitemaps.org/schemas/sitemap/0.9 "
            "http://www.sitemaps.org/schemas/sitemap/0.9/siteindex.xsd",
            "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        },
    )

    for i in range(1, number_of_batches + 1):
        sitemap = ET.SubElement(root, "sitemap")
        loc = ET.SubElement(sitemap, "loc")
        loc.text = (
            sitemap_config["loc_prefix"]
            + sitemap_config["file_prefix"]
            + str(i)
            + get_sitemap_file_suffix(sitemap_config)
        )

    save_sitemaps_file(root, sitemap_config["file_prefix"], context, sitemap_config)


def generate_sitemaps_file(batch, name, context, sitemap_config):
    root = ET.Element(
        "urlset",
        attrib={
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.sitemaps.org/schemas/sitemap/0.9 "
            "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd",
            "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        },
    )

    for entry in batch:
        url = ET.SubElement(root, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = sitemap_config["loc_prefix"] + entry["output"]

    save_sitemaps_file(root, name, context, sitemap_config)


def generate_sitemaps(data, context, config):
    sitemaps_config = sitemaps_default_config()
    sitemaps_config.update(config.get("sitemaps", {}))

    batches = get_files_to_map(data, sitemaps_config)
    if len(batches) > 1:
        logger.info("Entry limit exceeded; generating index file...")
        generate_index_file(context, sitemaps_config, len(batches))
        for i, batch in enumerate(batches):
            generate_sitemaps_file(
                batch,
                sitemaps_config["file_prefix"] + str(i + 1),
                context,
                sitemaps_config,
            )
    if len(batches) == 1:
        generate_sitemaps_file(
            batches[0], sitemaps_config["file_prefix"], context, sitemaps_config
        )
