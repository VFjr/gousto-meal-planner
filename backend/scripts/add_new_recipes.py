"""
Script to add all new recipes to the database
"""

import httpx
import asyncio

BASE_URL = "http://127.0.0.1:8000"  # Adjust the base URL as needed

async def fetch_new_recipes():
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(f"{BASE_URL}/recipes/check-new")
        response.raise_for_status()
        return response.json()

async def add_recipe(slug):
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(f"{BASE_URL}/recipes/add/{slug}")
        response.raise_for_status()
        return response.json()

async def main():
    print("Fetching list of recipes to add...")
    new_recipes_data = await fetch_new_recipes()
    new_recipe_slugs = new_recipes_data.get("new_recipe_slugs", [])
    total_recipes = len(new_recipe_slugs)

    print(f"Found {total_recipes} new recipes to add")

    semaphore = asyncio.Semaphore(20) 
    
    async def add_recipe_with_semaphore(slug, index):
        async with semaphore:
            try:
                added_recipe = await add_recipe(slug)
                print(f"[{index}/{total_recipes}] Successfully added recipe: {added_recipe['title']}")
            except httpx.HTTPStatusError as e:
                print(f"[{index}/{total_recipes}] Failed to add recipe with slug '{slug}': {e.response.text}")

    tasks = [add_recipe_with_semaphore(slug, i) for i, slug in enumerate(new_recipe_slugs, 1)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
