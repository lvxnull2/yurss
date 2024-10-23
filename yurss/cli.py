import argparse
import os.path
from itertools import islice
from pathlib import Path, PurePath
from sys import argv, exit
from typing import no_type_check
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup

from . import config
from .lib import Article, SortType


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

    return islice(sorted(Path(path).iterdir(), key=key, reverse=True), n)


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

    if og_title := head.find("meta", property="og:title", recursive=False):
        title = og_title["content"]
    elif html_title := head.title:
        title = html_title.string
    else:
        title = path.name

    if og_description := head.find("meta", property="og:description", recursive=False):
        description = og_description["content"]

    if og_author := head.find("meta", property="og:author", recursive=False):
        author = og_author["content"]

    return Article(
        title=title,
        url=url,
        description=description,
        author=author,
    )


def main():
    parser = argparse.ArgumentParser(description="rss feed generator")
    args = parser.parse_args(argv)
    return 0
