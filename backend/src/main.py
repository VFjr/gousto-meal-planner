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
    RecipeSummary,
    IngredientSummary,
    BadRecipeSlug,
    RecipeCheckResult,
)
from .gousto_fetcher import get_recipe_from_slug, get_all_recipe_slugs
from .database import get_session
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.post("/recipes/add/{slug}", response_model=RecipePublic)
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


@app.get("/recipes/list", response_model=List[RecipeSummary])
async def list_recipes(session: AsyncSession = Depends(get_session)):
    """
    Get a list of all recipe slugs and names.
    """
    statement = select(Recipe.slug, Recipe.title)
    result = await session.exec(statement)
    recipes = result.all()
    return recipes


@app.delete("/recipes/delete/{slug}")
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


@app.get("/recipes/slug/{slug}", response_model=RecipePublic)
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


@app.get("/recipes/id/{recipe_id}", response_model=RecipePublic)
async def get_recipe_by_id(
    recipe_id: int, session: AsyncSession = Depends(get_session)
):
    """
    Get a recipe by its ID.
    """
    statement = (
        select(Recipe)
        .where(Recipe.id == recipe_id)
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
            status_code=404, detail=f"Recipe with ID '{recipe_id}' not found"
        )

    return recipe


@app.get("/ingredients/list", response_model=List[IngredientSummary])
async def list_ingredients(session: AsyncSession = Depends(get_session)):
    """
    Get a list of all ingredient names and ids.
    """
    statement = select(Ingredient.name, Ingredient.id)
    result = await session.exec(statement)
    ingredients = result.all()
    return ingredients


@app.get("/recipes/by-ingredient/{ingredient_id}", response_model=List[RecipeSummary])
async def get_recipes_by_ingredient_id(
    ingredient_id: int, session: AsyncSession = Depends(get_session)
):
    """
    Get all recipes that include a specific ingredient by its ID.
    """
    # Query to find all recipe links with the given ingredient ID
    statement = (
        select(Recipe)
        .join(RecipeIngredientLink)
        .where(RecipeIngredientLink.ingredient_id == ingredient_id)
    )
    result = await session.exec(statement)
    recipes = result.all()

    if not recipes:
        raise HTTPException(
            status_code=404,
            detail=f"No recipes found with ingredient ID '{ingredient_id}'",
        )

    return recipes


@app.get("/recipes/check-new", response_model=RecipeCheckResult)
async def check_new_recipes(session: AsyncSession = Depends(get_session)):
    """
    Fetch all recipes from Gousto, compare with existing ones, and return lists of new and previously bad recipe slugs
    """
    try:
        # Fetch all recipe stubs from Gousto
        gousto_recipes = await get_all_recipe_slugs(max_concurrent_requests=50)

        # Fetch all existing recipes from the database
        statement = select(Recipe.slug)
        result = await session.exec(statement)
        existing_recipes = result.all()

        # Fetch all bad recipe slugs from the database
        bad_slug_statement = select(BadRecipeSlug.slug)
        bad_slug_result = await session.exec(bad_slug_statement)
        bad_recipe_slugs = bad_slug_result.all()

        gousto_set = set(gousto_recipes)
        existing_set = set(existing_recipes)
        bad_slugs_set = set(bad_recipe_slugs)

        potentially_new_recipes = gousto_set - existing_set
        new_recipe_slugs = potentially_new_recipes - bad_slugs_set
        previously_bad_recipe_slugs = potentially_new_recipes & bad_slugs_set

        return RecipeCheckResult(
            new_recipe_slugs=list(new_recipe_slugs),
            previously_bad_recipe_slugs=list(previously_bad_recipe_slugs),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing recipes: {e}") from e


# fetch recipes from gousto api
# will take a while, will return a list of changed recipes.
# modified
# updated

# apply temporary changes to db
# returns json with following fields/
# modified
# updated


# get recipe list by ingredient name
