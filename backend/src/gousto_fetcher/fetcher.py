from .constants import (
    GET_RECIPES_ENDPOINT,
    GET_RECIPE_INFO_ENDPOINT,
    GET_RECIPES_PAGE_LIMIT,
)
from .errors import NoMoreRecipesError
from .utils import page_to_offset, strip_recipes_prefix
from .models import Recipe
from .parser import parse_recipe
import aiohttp
import asyncio
import json
import logging


# async def get_recipe_slugs_from_page(page: int) -> list[str]:
#     """
#     Takes a page number and returns a list of recipe slugs

#     Raises:
#         aiohttp.ClientResponseError: If the response status code is not 200.
#         NoMoreRecipesError: If there are no more recipes to scrape.
#     """
#     logging.debug(f"Scraping page {page}")

#     offset = page_to_offset(page)

#     api_url = f"{GET_RECIPES_ENDPOINT}&limit={GET_RECIPES_PAGE_LIMIT}&offset={offset}"

#     async with aiohttp.ClientSession() as session:
#         async with session.get(api_url) as response:
#             if response.status != 200:
#                 raise aiohttp.ClientResponseError(
#                     request_info=response.request_info,
#                     history=response.history,
#                     status=response.status,
#                     message=f"HTTP error occurred: {response.status}",
#                 )

#             data = await response.json()
#             entries = data["data"]["entries"]
#             recipe_slug_list: list[str] = []

#             # check if there are any more recipes to scrape
#             if len(entries) == 0:
#                 raise NoMoreRecipesError

#             for entry in entries:
#                 slug = strip_recipes_prefix(entry["url"])
#                 recipe_slug_list.append(slug)

#             return recipe_slug_list


# async def get_all_recipe_slugs(max_concurrent_requests=5) -> list[str]:
#     page = 0
#     all_recipe_slugs: list[str] = []

#     while True:
#         try:
#             # Create a set of tasks, respecting the max concurrency limit
#             tasks = [
#                 get_recipe_slugs_from_page(page + i)
#                 for i in range(max_concurrent_requests)
#             ]

#             # Execute tasks concurrently
#             results = await asyncio.gather(*tasks, return_exceptions=True)

#             page_completed = False
#             for result in results:
#                 if isinstance(result, NoMoreRecipesError):
#                     # Stop further processing if we encounter a `NoMoreRecipesError`
#                     page_completed = True
#                     continue
#                 elif isinstance(result, Exception):
#                     # Handle other exceptions if necessary
#                     logging.error(f"Error occurs: {result}")
#                 else:
#                     all_recipe_slugs.extend(result)

#             if page_completed:
#                 break

#             page += max_concurrent_requests
#         except NoMoreRecipesError:
#             break

#     return all_recipe_slugs


async def get_recipe_from_slug(slug: str) -> Recipe:
    """
    Takes a recipe slug and returns its decoded Recipe directly from the Gousto API response

    Args:
        url: The url recipe slug of the recipe to scrape

    Raises:
        aiohttp.ClientResponseError: If the response status code is not 200.
    """
    api_url = f"{GET_RECIPE_INFO_ENDPOINT}{slug}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status != 200:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"HTTP error occurred: {response.status}",
                )

            data = await response.json()

            recipe = parse_recipe(data)

            return recipe
