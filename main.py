#!/usr/bin/env python3

import os.path
from datetime import datetime, timezone
from email.utils import format_datetime
from itertools import islice
from pathlib import Path, PurePath
from sys import argv
from urllib.parse import urlparse, urlunparse

from lxml import etree
from lxml.builder import E

import config
from lib import Article, SortType, Website


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
            E.generator(":3"),
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


def article_from_file(path: PurePath) -> Article:
    url = path2url(path)
    if not url:
        # TODO: handle the error more sensibly
        exit(100)

    # TODO: More sophisticated data collection
    return Article(
        title=path.name,
        url=url,
    )


if __name__ == "__main__":
    l = [article_from_file(p.resolve()) for p in find_latest(argv[1], 5)]
    print(etree.tostring(rss(config.website, l), encoding=str, pretty_print=True))
