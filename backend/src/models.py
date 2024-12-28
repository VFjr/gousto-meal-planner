from sqlmodel import SQLModel, Field, Relationship, JSON
from typing import List, Optional

class Ingredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class RecipeIngredientLink(SQLModel, table=True):
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id", primary_key=True)
    ingredient_id: Optional[int] = Field(default=None, foreign_key="ingredient.id", primary_key=True)
    amount: str

class InstructionStep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    images: Optional[dict[int, str]] = Field(default=None, sa_column=JSON) # key is image width, value is image url
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id")

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    gousto_id: Optional[str] = Field(default=None)
    gousto_uid: Optional[str] = Field(default=None)
    rating: Optional[float] = Field(default=None)
    prep_time: Optional[int] = Field(default=None)  # in minutes
    ingredients: List["RecipeIngredientLink"] = Relationship(back_populates="recipe")
    instruction_steps: List["InstructionStep"] = Relationship(back_populates="recipe")

RecipeIngredientLink.recipe = Relationship(back_populates="ingredients")
RecipeIngredientLink.ingredient = Relationship(back_populates="recipes")

Ingredient.recipes = Relationship(back_populates="ingredient", link_model=RecipeIngredientLink) 

InstructionStep.recipe = Relationship(back_populates="instruction_steps") 