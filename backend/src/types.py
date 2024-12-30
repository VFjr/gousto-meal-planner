from pydantic import BaseModel
from typing import List

class RecipeChangeList(BaseModel):
    modified: List[str] # list of recipe names
    updated: List[str]

class RecipeSlug(BaseModel):
    # slug from the url of recipe. Used in Gousto's API to get recipe info
    slug: str