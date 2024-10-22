from dataclasses import dataclass
from enum import Enum


@dataclass(slots=True)
class Article:
    title: str
    url: str
    description: str | None = None
    author: str | None = None


@dataclass(slots=True)
class Website:
    title: str
    url: str
    description: str
    language: str | None = None


class SortType(Enum):
    TIME = 1
    ALPHA = 2
