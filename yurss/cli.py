import argparse
import os.path
import re
from heapq import nlargest
from pathlib import Path, PurePath
from sys import exit
from typing import no_type_check
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup

from . import config
from .lib import Article, Person, SortType
from .rss import rss
from .util import fromisoformat, fromtimestamp, load_config, write_xml


def path2url(path) -> str | None:
    path = Path(path)
    for root in config.rootmap:
        try:
            relpath = path.relative_to(root)
        except ValueError:
            continue

        parsed = urlparse(config.rootmap[root])
        path = str(PurePath(parsed.path) / relpath)
        return urlunparse(parsed._replace(path=path))


def find_latest(path, n=5):
    key = None
    if config.sort == SortType.TIME:
        key = os.path.getmtime

    if n == 1:
        return [max(Path(path).iterdir(), key=key)]

    return nlargest(n, Path(path).iterdir(), key=key)


@no_type_check
def article_from_file(path) -> Article:
    path = Path(path)
    if path.is_dir():
        html_path = path / "index.html"
    else:
        html_path = path

    with open(html_path, "rb") as f:
        bs = BeautifulSoup(f, "lxml")

    if (head := bs.head) is None:
        # idk do something
        exit(100)

    url = path2url(path)
    if not url:
        # TODO: handle errors better
        exit(100)

    title = None
    description = None
    author = None
    pubTime = None
    modTime = None

    if og_title := head.find("meta", property="og:title", recursive=False):
        title = og_title["content"]
    elif html_title := head.title:
        title = html_title.string
    else:
        title = path.name

    if og_description := head.find("meta", property="og:description", recursive=False):
        description = og_description["content"]

    # Apparently, og:author is supposed to be a URL
    # but i dont care tbh, but for compatibility I will ignore a URL author.
    if og_author := head.find("meta", property="og:author", recursive=False):
        author_str = og_author["content"]
        if re.match("https?://", author_str) is None:
            author = Person.from_string(author_str)

    if og_pubTime := head.find(
        "meta", property="article:published_time", recursive=False
    ):
        pubTime = fromisoformat(og_pubTime["content"])

    if og_modTime := head.find(
        "meta", property="article:modified_time", recursive=False
    ):
        modTime = fromisoformat(og_modTime["content"])
    else:
        modTime = fromtimestamp(os.path.getmtime(html_path))

    return Article(
        title=title,
        url=url,
        description=description,
        author=author,
        published_date=pubTime,
        modified_date=modTime,
    )


def main():
    parser = argparse.ArgumentParser(description="rss feed generator")

    # fmt: off
    parser.add_argument(
        "--output", "-o",
        help="Path to output file. Stdout by default.",
        default="-",
        metavar="PATH",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["rss", "atom"],
        default="rss",
    )

    parser.add_argument(
        "--config", "-c",
        required=True,
        help="Path to config file.",
        metavar="PATH",
    )

    parser.add_argument(
        "--pretty-print",
        action="store_true",
        help="Generate XML with intendation",
    )

    parser.add_argument("directory")
    # fmt: on

    args = parser.parse_args()
    if args.format == "atom":
        print("Sorry, atom is currently unsupported")
        exit(1)

    load_config(args.config)
    articles = [article_from_file(f.resolve()) for f in find_latest(args.directory)]

    write_xml(
        rss(config.website, articles), args.output, pretty_print=args.pretty_print
    )

    return 0
