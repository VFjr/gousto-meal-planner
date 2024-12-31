from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import Recipe, RecipePublic, Ingredient, ImageLink, InstructionStep, RecipeIngredientLink
from .gousto_fetcher import get_recipe_info_from_slug
from .database import get_session
from typing import List
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
        recipe_data = await get_recipe_info_from_slug(slug)
        
        # Ingredients
        ingredient_obj_amount_list = []
        ingredient_list_data = recipe_data["ingredients"]
        for ingredient_data in ingredient_list_data:
            ingredient_name = ingredient_data["name"]

            # janky but i think this works
            ingredient_amount = ingredient_data["label"].replace(ingredient_name, "").strip()

            statement = select(Ingredient).where(Ingredient.name == ingredient_name)
            result = await session.exec(statement)
            existing_ingredient = result.one_or_none()

            if existing_ingredient:
                ingredient_obj = existing_ingredient
            else:
                ingredient_obj = Ingredient(name=ingredient_name)
                session.add(ingredient_obj)

                image_list_data = ingredient_data["media"]["images"]
                for image_data in image_list_data:
                    image_url = image_data["image"]
                    image_width = image_data["width"]

                    image_obj = ImageLink(url=image_url, width=image_width, ingredient=ingredient_obj)
                    session.add(image_obj)

            ingredient_obj_amount_list.append((ingredient_obj, ingredient_amount))


        # Instruction Steps
        instruction_step_obj_list = []

        instruction_step_list_data = recipe_data["cooking_instructions"]
        for instruction_step_data in instruction_step_list_data:
            instruction_step_text = instruction_step_data["instruction"]
            instruction_step_order = instruction_step_data["order"]

            instruction_step_obj = InstructionStep(text=instruction_step_text, order=instruction_step_order)
            session.add(instruction_step_obj)

            image_list_data = instruction_step_data["media"]["images"]
            for image_data in image_list_data:
                image_url = image_data["image"]
                image_width = image_data["width"]

                image_obj = ImageLink(url=image_url, width=image_width, instruction_step=instruction_step_obj)
                session.add(image_obj)

            instruction_step_obj_list.append(instruction_step_obj)
        
        title = recipe_data["title"]
        gousto_uid = recipe_data["gousto_uid"]
        rating = recipe_data["rating"]["average"]
        prep_time = recipe_data["prep_times"]["for_2"]

        basic_ingredients_data = recipe_data["basics"]
        basic_ingredients = [ingredient["title"] for ingredient in basic_ingredients_data]

        recipe_obj = Recipe(title=title, slug=slug,gousto_uid=gousto_uid, rating=rating, prep_time=prep_time, basic_ingredients=basic_ingredients, instruction_steps=instruction_step_obj_list)

        recipe_image_list_data = recipe_data["media"]["images"]
        for recipe_image_data in recipe_image_list_data:
            image_url = recipe_image_data["image"]
            image_width = recipe_image_data["width"]

            image_obj = ImageLink(url=image_url, width=image_width, recipe=recipe_obj)
            session.add(image_obj)

        # update link objects
        for ingredient_obj, ingredient_amount in ingredient_obj_amount_list:
            link_obj = RecipeIngredientLink(recipe=recipe_obj, ingredient=ingredient_obj, amount=ingredient_amount)
            session.add(link_obj)

        await session.commit()
        await session.refresh(recipe_obj)

        return recipe_obj
    except Exception as e:
        # Catch the error and raise an HTTPException 
        # so FastAPI won't try to validate a partial/different response
        import traceback
        print(f"Error in add_recipe_to_db: {e}")
        print(f"Type of error: {type(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Could not add recipe: {e}")









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