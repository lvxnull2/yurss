import runpy
from datetime import datetime, timezone
from sys import stdout

from lxml import etree
from lxml.etree import ElementTree

from . import config


def write_xml(xml, f: str, pretty_print=False):
    if f == "-":
        stdout.buffer.write(
            etree.tostring(
                xml, encoding="utf-8", xml_declaration=True, pretty_print=pretty_print
            )
        )
    else:
        ElementTree(xml).write(
            f, encoding="utf-8", xml_declaration=True, pretty_print=pretty_print
        )


def load_config(path):
    vars = runpy.run_path(path)

    for k, v in vars.items():
        if k.startswith("_"):
            continue
        setattr(config, k, v)

    return config


def now():
    return datetime.now(timezone.utc)
