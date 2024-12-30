from gousto_fetcher.constants import GET_RECIPES_PAGE_LIMIT

def page_to_offset(page: int) -> int:
    return page * GET_RECIPES_PAGE_LIMIT

def strip_recipes_prefix(url: str) -> str:
    """
    Strips the prefix "/recipes/" in url returned by API
    """
    if not url.startswith("/recipes/"):
        raise ValueError("url must start with /recipes/")
    return url[len("/recipes/"):]
