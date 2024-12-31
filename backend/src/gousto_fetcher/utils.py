from .constants import GET_RECIPES_PAGE_LIMIT
import re


def page_to_offset(page: int) -> int:
    return page * GET_RECIPES_PAGE_LIMIT


def strip_recipes_prefix(url: str) -> str:
    """
    Strips the prefix "/recipes/" or variations of it such as "/chicken-recipes/" in url returned by API
    """
    pattern = r"^/[^/]*recipes/"
    if not re.match(pattern, url):
        raise ValueError(
            f"url must start with a valid prefix followed by a sub-path, got {url}"
        )
    return re.sub(r"^/([^/]+-)?recipes/", "", url)
