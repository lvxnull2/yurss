from lib import SortType, Website

website: Website

rootmap: dict[str, str]
"""
Map of root directories to their URLs. Used to determine URLs of contained
files.
"""

sort: SortType
