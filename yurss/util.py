import runpy
from datetime import datetime, timezone
from sys import stdout

from lxml import etree

from . import config


def write_xml(xml, path: str, pretty_print=False):
    serialized = etree.tostring(
        xml, encoding="utf-8", xml_declaration=True, pretty_print=pretty_print
    )

    if path == "-":
        stdout.buffer.write(serialized)
        return

    with open(path, "wb") as f:
        f.write(serialized)


def load_config(path):
    vars = runpy.run_path(path)

    for k, v in vars.items():
        if k.startswith("_"):
            continue
        setattr(config, k, v)

    return config


def now():
    return datetime.now(timezone.utc)


def fromisoformat(s: str):
    return datetime.fromisoformat(s).astimezone(timezone.utc)
