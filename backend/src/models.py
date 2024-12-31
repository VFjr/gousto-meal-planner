from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from pydantic import BaseModel
from typing import List, Optional


# Image Link
class ImageURLBase(SQLModel):
    width: int
    url: str


class ImageURL(ImageURLBase, table=True):
    __tablename__ = "image_link"
    id: int | None = Field(default=None, primary_key=True)
    ingredient: Optional["Ingredient"] = Relationship(back_populates="images")
    ingredient_id: Optional[int] = Field(default=None, foreign_key="ingredient.id")
    instruction_step: Optional["InstructionStep"] = Relationship(
        back_populates="images"
    )
    instruction_step_id: Optional[int] = Field(
        default=None, foreign_key="instruction_step.id"
    )
    recipe: Optional["Recipe"] = Relationship(back_populates="images")
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id")


class ImageURLPublic(ImageURLBase):
    id: int


## RecipeIngredientLink Models


class RecipeIngredientLinkBase(SQLModel):
    amount: str


class RecipeIngredientLink(RecipeIngredientLinkBase, table=True):
    __tablename__ = "recipe_ingredient_link"
    recipe_id: int | None = Field(
        default=None, foreign_key="recipe.id", primary_key=True, ondelete="CASCADE"
    )
    ingredient_id: int | None = Field(
        default=None, foreign_key="ingredient.id", primary_key=True
    )

    recipe: "Recipe" = Relationship(back_populates="ingredients")
    ingredient: "Ingredient" = Relationship(back_populates="recipe_links")


class RecipeIngredientLinkPublic(RecipeIngredientLinkBase):
    ingredient: "IngredientPublic"


## Ingredient Models
class IngredientBase(SQLModel):
    name: str


class Ingredient(IngredientBase, table=True):
    __tablename__ = "ingredient"
    id: int | None = Field(default=None, primary_key=True)
    images: List[ImageURL] = Relationship(
        back_populates="ingredient", cascade_delete=True
    )
    recipe_links: List[RecipeIngredientLink] = Relationship(back_populates="ingredient")


class IngredientPublic(IngredientBase):
    id: int
    images: List[ImageURLPublic] = []


## Instruction Step Models
class InstructionStepBase(SQLModel):
    text: str
    order: int
    recipe_id: int = Field(default=None, foreign_key="recipe.id", ondelete="CASCADE")


class InstructionStep(InstructionStepBase, table=True):
    __tablename__ = "instruction_step"

    id: int | None = Field(default=None, primary_key=True)
    recipe: "Recipe" = Relationship(back_populates="instruction_steps")
    images: List["ImageURL"] = Relationship(
        back_populates="instruction_step", cascade_delete=True
    )


class InstructionStepPublic(InstructionStepBase):
    id: int
    images: List[ImageURLPublic] = []


## Recipe Models
class BaseRecipe(SQLModel):
    title: str
    slug: str
    gousto_uid: Optional[str] = Field(default=None)
    rating: Optional[float] = Field(default=None)
    prep_time: Optional[int] = Field(
        default=None
    )  # in minutes, using the for_two field


class Recipe(BaseRecipe, table=True):
    __tablename__ = "recipe"
    id: int | None = Field(default=None, primary_key=True)

    basic_ingredients: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),  # or sa_column=Column(JSONB) if you prefer
    )

    ingredients: List[RecipeIngredientLink] = Relationship(
        back_populates="recipe", cascade_delete=True
    )
    instruction_steps: List[InstructionStep] = Relationship(
        back_populates="recipe", cascade_delete=True
    )
    images: List[ImageURL] = Relationship(back_populates="recipe", cascade_delete=True)


class RecipePublic(BaseRecipe):
    id: int
    basic_ingredients: List[str] = []
    instruction_steps: List[InstructionStepPublic] = []
    images: List[ImageURLPublic] = []
    ingredients: List[RecipeIngredientLinkPublic] = []

class RecipeSummary(SQLModel):
    slug: str
    title: str

class RecipeChangeList(BaseModel):
    modified: List[str]  # list of recipe names
    updated: List[str]