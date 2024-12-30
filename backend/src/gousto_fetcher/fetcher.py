from gousto_fetcher.constants import GET_RECIPES_ENDPOINT,GET_RECIPE_INFO_ENDPOINT, GET_RECIPES_PAGE_LIMIT
from gousto_fetcher.errors import NoMoreRecipesError
from gousto_fetcher.utils import page_to_offset, strip_recipes_prefix
from ..models import RecipeURL
import aiohttp
import asyncio
import json
import logging

async def get_recipe_links_from_page(page: int) -> list[RecipeURL]:
    """
    Takes a page number and returns a list of recipe links

    Raises:
        aiohttp.ClientResponseError: If the response status code is not 200.
        NoMoreRecipesError: If there are no more recipes to scrape.
    """
    logging.debug(f"Scraping page {page}")

    offset = page_to_offset(page)
    
    api_url = f"{GET_RECIPES_ENDPOINT}&limit={GET_RECIPES_PAGE_LIMIT}&offset={offset}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status != 200:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"HTTP error occurred: {response.status}"
                )
            
            data = await response.json()
            entries = data["data"]["entries"]
            recipe_url_list : list[RecipeURL] = []

            # check if there are any more recipes to scrape
            if len(entries) == 0:
                raise NoMoreRecipesError

            for entry in entries:
                recipe_url_list.append(RecipeURL(url=entry["url"]))
            
            return recipe_url_list

async def get_all_recipes(max_concurrent_requests=5) -> list[RecipeURL]:
    page = 0
    all_recipes : list[RecipeURL] = []

    while True:
        try:
            # Create a set of tasks, respecting the max concurrency limit
            tasks = [
                get_recipe_links_from_page(page + i)
                for i in range(max_concurrent_requests)
            ]

            # Execute tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            page_completed = False
            for result in results:
                if isinstance(result, NoMoreRecipesError):
                    # Stop further processing if we encounter a `NoMoreRecipesError`
                    page_completed = True
                    continue
                elif isinstance(result, Exception):
                    # Handle other exceptions if necessary
                    logging.error(f"Error occurs: {result}")
                else:
                    all_recipes.extend(result)

            if page_completed:
                break

            page += max_concurrent_requests
        except NoMoreRecipesError:
            break

    return all_recipes
        
async def get_recipe_info_from_link(url: str) -> RecipeInfo:
    """
    Takes a recipe url and returns a RecipeInfo object

    Args:
        url: The url of the recipe to scrape. Is in the format returned by get_recipe_links_from_page, which is of the form "/recipes/{recipe_name}"

    Raises:
        aiohttp.ClientResponseError: If the response status code is not 200.
    """
    url = strip_recipes_prefix(url)
    print(f"stripped_url: {url}")

    api_url = f"{GET_RECIPE_INFO_ENDPOINT}{url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status != 200:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"HTTP error occurred: {response.status}"
                )
            
            data = await response.json()
            
            ingredients = [ingredient["label"] for ingredient in data["entry"]["ingredients"]]

            recipe_info = RecipeInfo(ingredients=ingredients)
            return recipe_info
    
    
    