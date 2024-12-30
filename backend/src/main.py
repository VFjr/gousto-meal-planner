from fastapi import FastAPI, Depends
from sqlmodel import Session
from .database import get_session
from .crud import get_recipe_by_id, update_recipes
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# fetch recipe slugs from gousto api
@app.get("/recipes/slugs", response_model=List[RecipeSlug])
async def fetch_recipe_slugs(page: int, session: Session = Depends(get_session)):
    """
    Fetch recipe slugs from Gousto API.
    """
    from .gousto_fetcher import get_recipe_slugs_from_page
    try:
        recipe_slugs = await get_recipe_slugs_from_page(page)
        return recipe_slugs
    except Exception as e:
        return {"error": str(e)}












# fetch recipes from gousto api
# will take a while, will return a list of changed recipes.
# modified
# updated

# apply temporary changes to db
# returns json with following fields/ 
# modified
# updated

# get complete list of recipes
# returns json with a full list of recipes, used to have browser side fuzzy search

# get complete list of ingredients
# returns json with a full list of ingredients, used to have browser side fuzzy search

# get recipe by name

# get recipe by url

# get recipe by id

# get recipe list by ingredient name