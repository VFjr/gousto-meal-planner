"""
Script to add all new recipes to the database
"""

# run with uv run ./scripts/add_new_recipes.py --username admin --password password

import asyncio
import argparse

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"  # Adjust the base URL as needed

# Replace the credentials section with argument parsing
parser = argparse.ArgumentParser(description='Add new recipes to the database')
parser.add_argument('--username', required=True, help='Admin username')
parser.add_argument('--password', required=True, help='Admin password')
args = parser.parse_args()

USERNAME = args.username
PASSWORD = args.password

if not USERNAME or not PASSWORD:
    raise ValueError("Username and password must be provided")


async def get_access_token():
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/token",
                data={"username": USERNAME, "password": PASSWORD},
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except httpx.HTTPStatusError as e:
            print(f"Failed to get access token: {e.response.text}")
            raise


async def fetch_new_recipes(token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f"{BASE_URL}/recipes/check-new",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()


async def add_recipe(slug: str, token: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{BASE_URL}/recipes/add/{slug}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()


async def main():
    print("Getting access token...")
    token = await get_access_token()

    print("Fetching list of recipes to add...")
    new_recipes_data = await fetch_new_recipes(token)
    new_recipe_slugs = new_recipes_data.get("new_recipe_slugs", [])
    total_recipes = len(new_recipe_slugs)

    print(f"Found {total_recipes} new recipes to add")

    semaphore = asyncio.Semaphore(2)

    async def add_recipe_with_semaphore(slug, index):
        async with semaphore:
            try:
                print(f"[{index}/{total_recipes}] Adding recipe with slug: {slug}")
                added_recipe = await add_recipe(slug, token)
                print(
                    f"[{index}/{total_recipes}] Successfully added recipe: {added_recipe['title']}"
                )
            except httpx.HTTPStatusError as e:
                print(
                    f"[{index}/{total_recipes}] Failed to add recipe with slug '{slug}': {e.response.text}"
                )

    tasks = [
        add_recipe_with_semaphore(slug, i) for i, slug in enumerate(new_recipe_slugs, 1)
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
