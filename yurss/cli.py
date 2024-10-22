#!/usr/bin/env python3

import os.path
import runpy
from datetime import datetime, timezone
from email.utils import format_datetime
from itertools import islice
from pathlib import Path, PurePath
from sys import argv, exit
from typing import no_type_check
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from lxml.builder import E

from . import config
from .lib import Article, SortType, Website


def load_config(path):
    vars = runpy.run_path(path)

    for k, v in vars.items():
        if k.startswith("_"):
            continue
        setattr(config, k, v)

    return config


def now():
    return datetime.now(timezone.utc)


def rss_article(article: Article):
    optional = []

    if article.description:
        optional.append(E.description(article.description))

    if article.author:
        optional.append(E.author(article.author))

    return E.item(
        E.title(article.title),
        E.link(article.url),
        *optional,
    )


def rss(website: Website, articles: list[Article]):
    optional = []

    # def optadd(attr: str, el: str | None = None, value: str | None = None):
    #     if v := getattr(website, attr):
    #         optional.append(getattr(E, el or attr)(value or str(v)))

    if website.language:
        optional.append(E.language(website.language))

    for a in articles:
        optional.append(rss_article(a))

    return E.rss(
        E.channel(
            E.title(website.title),
            E.link(website.url),
            E.description(website.description),
            E.generator("yurss"),
            E.lastBuildDate(format_datetime(now(), usegmt=True)),
            *optional,
        ),
        version="2.0",
    )


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
    print(argv)
    return 0
