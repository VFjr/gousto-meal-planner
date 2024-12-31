from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from .models import (
    Recipe,
    RecipePublic,
    Ingredient,
    ImageURL,
    InstructionStep,
    RecipeIngredientLink,
)
from .gousto_fetcher import get_recipe_from_slug
from .database import get_session
from typing import List, Tuple
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# fetch recipe slugs from gousto api
# @app.get("/recipes/slugs", response_model=List[RecipeSlug])
# async def fetch_recipe_slugs(page: int, session: Session = Depends(get_session)):
#     """
#     Fetch recipe slugs from Gousto API.
#     """
#     from .gousto_fetcher import get_recipe_slugs_from_page
#     try:
#         recipe_slugs = await get_recipe_slugs_from_page(page)
#         return recipe_slugs
#     except Exception as e:
#         return {"error": str(e)}


@app.post("/add_recipe/{slug}", response_model=RecipePublic)
async def add_recipe_to_db(slug: str, session: AsyncSession = Depends(get_session)):
    """
    Add a recipe to the database using its Gousto slug.
    """
    try:
        # Check if recipe already exists
        statement = select(Recipe).where(Recipe.slug == slug)
        result = await session.exec(statement)
        existing_recipe = result.one_or_none()

        if existing_recipe:
            raise HTTPException(
                status_code=409, detail="Recipe with this slug already exists"
            )

        recipe_data = await get_recipe_from_slug(slug)

        # Ingredients
        ingredient_obj_amount_list: List[Tuple[Ingredient, str]] = []

        for ingredient_data in recipe_data.ingredients:
            statement = select(Ingredient).where(
                Ingredient.name == ingredient_data.name
            )
            result = await session.exec(statement)
            existing_ingredient = result.one_or_none()

            if existing_ingredient:
                ingredient_obj = existing_ingredient
            else:
                ingredient_obj = Ingredient(name=ingredient_data.name)

                session.add(ingredient_obj)

                for image_data in ingredient_data.image_urls:
                    image_obj = ImageURL(
                        url=image_data.url,
                        width=image_data.width,
                        ingredient=ingredient_obj,
                    )
                    session.add(image_obj)

            # Needed for link objects
            ingredient_obj_amount_list.append((ingredient_obj, ingredient_data.amount))

        # Instruction Steps
        instruction_step_obj_list = []

        for instruction_step_data in recipe_data.instruction_steps:
            instruction_text = instruction_step_data.description
            order = instruction_step_data.step_number

            instruction_step_obj = InstructionStep(text=instruction_text, order=order)
            session.add(instruction_step_obj)

            for image_data in instruction_step_data.image_urls:
                image_obj = ImageURL(
                    url=image_data.url,
                    width=image_data.width,
                    instruction_step=instruction_step_obj,
                )
                session.add(image_obj)

            instruction_step_obj_list.append(instruction_step_obj)

        recipe_obj = Recipe(
            title=recipe_data.title,
            slug=slug,
            gousto_uid=recipe_data.gousto_uid,
            rating=recipe_data.rating,
            prep_time=recipe_data.prep_time,
            basic_ingredients=recipe_data.basic_ingredients,
            instruction_steps=instruction_step_obj_list,
        )

        for recipe_image_data in recipe_data.images:
            image_obj = ImageURL(
                url=recipe_image_data.url,
                width=recipe_image_data.width,
                recipe=recipe_obj,
            )
            session.add(image_obj)

        # update link objects
        for ingredient_obj, ingredient_amount in ingredient_obj_amount_list:
            link_obj = RecipeIngredientLink(
                recipe=recipe_obj, ingredient=ingredient_obj, amount=ingredient_amount
            )
            session.add(link_obj)

        await session.commit()
        await session.refresh(recipe_obj)

        # Re-query the newly created recipe with eager loading:
        stmt = (
            select(Recipe)
            .options(
                selectinload(Recipe.instruction_steps).options(
                    selectinload(InstructionStep.images)
                ),
                selectinload(Recipe.ingredients).options(
                    selectinload(RecipeIngredientLink.ingredient).options(
                        selectinload(Ingredient.images)
                    )
                ),
                selectinload(Recipe.images),
            )
            .where(Recipe.id == recipe_obj.id)
        )
        result = await session.exec(stmt)
        fresh_recipe_obj = result.one()
        return fresh_recipe_obj

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not add recipe: {e}") from e


@app.get("/recipes/{slug}", response_model=RecipePublic)
async def get_recipe_by_slug(slug: str, session: AsyncSession = Depends(get_session)):
    """
    Get a recipe by its slug.
    """
    statement = (
        select(Recipe)
        .where(Recipe.slug == slug)
        .options(
            # Eager-load instruction steps + their images
            selectinload(Recipe.instruction_steps).selectinload(InstructionStep.images),
            # Eager-load recipe images
            selectinload(Recipe.images),
            # Eager-load ingredient links and their associated ingredient objects & images
            selectinload(Recipe.ingredients)
            .selectinload(RecipeIngredientLink.ingredient)
            .selectinload(Ingredient.images),
        )
    )
    result = await session.exec(statement)
    recipe = result.one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=404, detail=f"Recipe with slug '{slug}' not found"
        )

    return recipe


@app.delete("/recipes/{slug}")
async def delete_recipe_by_slug(
    slug: str, session: AsyncSession = Depends(get_session)
):
    """
    Delete a recipe by its slug.
    """
    # Find the recipe by slug
    statement = select(Recipe).where(Recipe.slug == slug)
    result = await session.exec(statement)
    recipe = result.one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=404, detail=f"Recipe with slug '{slug}' not found."
        )

    # If found, delete it
    await session.delete(recipe)
    await session.commit()

    return {"ok": True, "message": f"Recipe '{slug}' has been deleted."}


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
