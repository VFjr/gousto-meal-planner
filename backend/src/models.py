from sqlmodel import SQLModel, Field, Relationship, JSON
from pydantic import BaseModel
from typing import List, Optional

## Ingredient Models
class IngredientBase(SQLModel):
    images: Optional[dict[int, str]] = Field(default=None, sa_column=JSON) # key is image width, value is image url
    name: str
    recipes: List["RecipeIngredientLink"] = Relationship(back_populates="ingredients", link_model=RecipeIngredientLink)

class Ingredient(IngredientBase, table=True):
    id: int | None= Field(default=None, primary_key=True)

class IngredientPublic(IngredientBase):
    id: int

## RecipeIngredientLink Models
class RecipeIngredientLink(SQLModel, table=True):
    recipe_id: int | None = Field(default=None, foreign_key="recipe.id", primary_key=True)
    ingredient_id: int | None = Field(default=None, foreign_key="ingredient.id", primary_key=True)
    amount: str

## Instruction Step Models
class InstructionStepBase(SQLModel):
    text: str
    images: Optional[dict[int, str]] = Field(default=None, sa_column=JSON) # key is image width, value is image url
    recipe_id: int = Field(default=None, foreign_key="recipe.id")
    recipe: "Recipe" = Relationship(back_populates="instruction_steps")
class InstructionStep(InstructionStepBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class InstructionStepPublic(InstructionStepBase):
    id: int

## Recipe Models
class BaseRecipe(SQLModel):
    title: str
    url: str
    gousto_uid: Optional[str] = Field(default=None)
    images: Optional[dict[int, str]] = Field(default=None, sa_column=JSON) # key is image width, value is image url
    rating: Optional[float] = Field(default=None)
    prep_time: Optional[int] = Field(default=None)  # in minutes, using the for_two field
    ingredients: List[RecipeIngredientLink] = Relationship(back_populates="recipe")
    instruction_steps: List[InstructionStep] = Relationship(back_populates="recipe")
    basic_ingredients: List[str] = Field(default=[])

class Recipe(BaseRecipe, table=True):
    id: int | None = Field(default=None, primary_key=True)

class NewRecipe(BaseRecipe, table=True):
    id: int | None = Field(default=None, primary_key=True) 

class RecipePublic(BaseRecipe):
    id: int

class RecipeChangeList(BaseModel):
    modified: List[str] # list of recipe names
    updated: List[str]

class RecipeURL(BaseModel):
    # url of recipe, in the form "/recipes/{recipe_name}" (as that's how the Gousto API returns it)
    url: str
