from fastapi import FastAPI, Depends
from sqlmodel import Session
from .database import get_session
from .crud import get_recipe_by_id, update_recipes
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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