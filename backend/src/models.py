from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from pydantic import BaseModel
from typing import List, Optional

# Image Link
class ImageLinkBase(SQLModel):
    width: int
    url: str

class ImageLink(ImageLinkBase, table=True):
    __tablename__ = "image_link"
    id: int | None = Field(default=None, primary_key=True)
    ingredient: Optional["Ingredient"] = Relationship(back_populates="images")
    ingredient_id: Optional[int] = Field(default=None, foreign_key="ingredient.id")
    instruction_step: Optional["InstructionStep"] = Relationship(back_populates="images")
    instruction_step_id: Optional[int] = Field(default=None, foreign_key="instruction_step.id")
    recipe: Optional["Recipe"] = Relationship(back_populates="images")
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id")


class ImageLinkPublic(ImageLinkBase):
    id: int


## RecipeIngredientLink Models
class RecipeIngredientLink(SQLModel, table=True):
    __tablename__ = "recipe_ingredient_link"
    recipe_id: int | None = Field(default=None, foreign_key="recipe.id", primary_key=True)
    ingredient_id: int | None = Field(default=None, foreign_key="ingredient.id", primary_key=True)
    amount: str

    recipe: "Recipe" = Relationship(back_populates="ingredient_links")
    ingredient: "Ingredient" = Relationship(back_populates="recipe_links")


## Ingredient Models
class IngredientBase(SQLModel):
    name: str

class Ingredient(IngredientBase, table=True):
    __tablename__ = "ingredient"
    id: int | None = Field(default=None, primary_key=True)
    images: List[ImageLink] = Relationship(back_populates="ingredient")
    recipe_links: List[RecipeIngredientLink] = Relationship(back_populates="ingredient")

class IngredientPublic(IngredientBase):
    id: int

## Instruction Step Models
class InstructionStepBase(SQLModel):
    text: str
    order: int
    recipe_id: int = Field(default=None, foreign_key="recipe.id")
    
class InstructionStep(InstructionStepBase, table=True):
    __tablename__ = "instruction_step"

    id: int | None = Field(default=None, primary_key=True)
    recipe: "Recipe" = Relationship(back_populates="instruction_steps")
    images: List["ImageLink"] = Relationship(back_populates="instruction_step")

class InstructionStepPublic(InstructionStepBase):
    id: int

## Recipe Models
class BaseRecipe(SQLModel):
    title: str
    slug: str
    gousto_uid: Optional[str] = Field(default=None)
    rating: Optional[float] = Field(default=None)
    prep_time: Optional[int] = Field(default=None)  # in minutes, using the for_two field
   
class Recipe(BaseRecipe, table=True):
    __tablename__ = "recipe"
    id: int | None = Field(default=None, primary_key=True)

    basic_ingredients: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON)  # or sa_column=Column(JSONB) if you prefer
    )

    ingredient_links: List[RecipeIngredientLink] = Relationship(back_populates="recipe")
    instruction_steps: List[InstructionStep] = Relationship(back_populates="recipe")
    images: List[ImageLink] = Relationship(back_populates="recipe")


class RecipePublic(BaseRecipe):
    id: int
    basic_ingredients: List[str] = []



class RecipeChangeList(BaseModel):
    modified: List[str] # list of recipe names
    updated: List[str]

class RecipeSlug(BaseModel):
    # slug from the url of recipe. Used in Gousto's API to get recipe info
    slug: str