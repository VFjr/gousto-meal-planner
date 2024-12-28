from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Ingredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ingredients: List[Ingredient] = Relationship(back_populates="recipe")

Ingredient.recipe = Relationship(back_populates="ingredients") 