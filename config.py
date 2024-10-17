from lib import SortType, Website

website = Website(
    title="Example title",
    url="https://example.com",
    description="Example description",
    language="en-us",
)

rootmap = {
    "/www/": "https://example.com/blog/",
}

sort = SortType.ALPHA
