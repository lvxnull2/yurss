from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(slots=True)
class Article:
    title: str
    url: str
    description: str | None = None
    author: str | None = None
    published_date: datetime | None = None
    modified_date: datetime | None = None


@dataclass(slots=True)
class Website:
    title: str
    url: str
    description: str
    language: str | None = None


class SortType(Enum):
    TIME = 1
    ALPHA = 2
