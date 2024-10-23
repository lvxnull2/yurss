from email.utils import format_datetime

from lxml.builder import E

from .lib import Article, Website
from .util import now


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