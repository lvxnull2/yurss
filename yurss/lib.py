import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(slots=True)
class Person:
    name: str
    email: str | None = None
    url: str | None = None

    @staticmethod
    def from_string(s: str) -> "Person":
        m = re.fullmatch("([^<]+) <([^>]+)>", s)
        if m is None:
            return Person(name=s)
        return Person(name=m[1], email=m[2])

    def __str__(self):
        if self.email == None:
            return self.name
        return f"{self.name} <{self.email}>"


@dataclass(slots=True)
class Article:
    title: str
    url: str
    modified_date: datetime
    published_date: datetime | None = None
    description: str | None = None
    author: Person | None = None


@dataclass(slots=True)
class Website:
    title: str
    url: str
    description: str
    language: str | None = None
    author: Person | None = None


class SortType(Enum):
    TIME = 1
    ALPHA = 2
