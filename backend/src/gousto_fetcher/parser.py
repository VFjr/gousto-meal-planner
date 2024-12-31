# functions that parse the data from the gousto api, and handle all its nuances

from .models import Recipe, ImageURL, Ingredient, InstructionStep
from typing import Optional, List
from collections import defaultdict

# ===== Recipe Parsing =====


def parse_recipe(recipe_data: dict) -> Recipe:
    """
    Parses the recipe info from the gousto api into a Recipe object

    Args:
        recipe_data: The recipe data from the gousto api as a dict. Should include all the data, includhing the ["data"]["entry"]
    """

    recipe_data = recipe_data["data"]["entry"]

    ingredient_list = parse_all_ingredients(recipe_data["ingredients"])
    instruction_steps = parse_all_instruction_steps(recipe_data["cooking_instructions"])
    image_urls = parse_image_urls(recipe_data["media"]["images"])

    title = recipe_data["title"]
    gousto_uid = recipe_data["gousto_uid"]
    rating = recipe_data["rating"]["average"]
    prep_time = recipe_data["prep_times"]["for_2"]

    basic_ingredients_data = recipe_data["basics"]
    basic_ingredients = [ingredient["title"] for ingredient in basic_ingredients_data]

    return Recipe(
        title=title,
        gousto_uid=gousto_uid,
        images=image_urls,
        rating=rating,
        prep_time=prep_time,
        ingredients=ingredient_list,
        instruction_steps=instruction_steps,
        basic_ingredients=basic_ingredients,
    )


# --- Ingredient Parsing ---


def parse_all_ingredients(ingredients_data: dict) -> List[Ingredient]:
    """
    Parses all the ingredients from the gousto api into a list of Ingredient objects

    Handles duplicated ingredients
    """

    # using a dict to later efficiently check for duplicates. Key is the ingredient name
    ingredient_dict: dict[str, List[Ingredient]] = defaultdict(list)

    for ingredient_data in ingredients_data:
        ingredient = parse_ingredient_data(ingredient_data)
        if ingredient:
            ingredient_dict[ingredient.name].append(ingredient)

    # iterate over the dict, check if there are duplicates
    for ingredient_name, ingredient_list in ingredient_dict.items():
        if len(ingredient_list) > 1:
            ingredient_dict[ingredient_name] = handle_duplicate_ingredients(
                ingredient_list
            )

    # Flatten the list of lists into a single list of ingredients
    return [
        ingredient
        for ingredient_list in ingredient_dict.values()
        for ingredient in ingredient_list
    ]


def handle_duplicate_ingredients(ingredient_list: List[Ingredient]) -> List[Ingredient]:
    """
    Handles duplicate ingredients in the list by keeping the most detailed ingredient
    As Gousto API can return duplicates of the same ingredient with different amounts

    Current supported rules:

    If one has a unit (g/ml) and one is just a number, keep the one with the unit

    Args:
        ingredient_list: List of the same ingredients
    """

    # if there's only one ingredient, return it
    if len(ingredient_list) == 1:
        return ingredient_list

    # Check if one has a unit (g/ml) and one is just a number
    amounts = [ingredient.amount for ingredient in ingredient_list]

    # Find amounts with units vs plain numbers
    unit_amounts = [amt for amt in amounts if any(unit in amt for unit in ["g", "ml"])]
    number_amounts = [amt for amt in amounts if amt.strip("1234567890") == ""]

    if len(unit_amounts) == 1 and len(number_amounts) == 1:
        # Keep the one with the unit
        for ingredient in ingredient_list:
            if any(unit in ingredient.amount for unit in ["g", "ml"]):
                return [ingredient]

    # If we get here, we don't know how to handle these duplicates
    raise ValueError(f"Unable to handle duplicate ingredients with amounts: {amounts}")


def parse_ingredient_data(ingredient_data: dict) -> Optional[Ingredient]:
    """
    Parses the ingredient data from the gousto api into an Ingredient object

    Returns None if the ingredient should be ignored (e.g quantity is 0)
    """

    name = ingredient_data["name"].lower()

    # get the amount. Janky but it works so far
    amount = ingredient_data["label"].lower().replace(name, "").strip()

    if amount == "0":
        return None

    image_urls = parse_image_urls(ingredient_data["media"]["images"])

    return Ingredient(name=name, amount=amount, image_urls=image_urls)


# --- ImageURL Parsing ---


def parse_image_urls(image_urls_data: List[dict]) -> List[ImageURL]:
    """
    Parses the image url data from the gousto api into a list of ImageURL objects

    Args: image_urls_data:
    """

    return [
        ImageURL(url=image_data["image"], width=image_data["width"])
        for image_data in image_urls_data
    ]


# --- Instruction Step Parsing ---

def parse_all_instruction_steps(instruction_steps_data: dict) -> List[InstructionStep]:
    """
    Parses all the instruction steps from the gousto api into a list of InstructionStep objects
    """

    instruction_steps = []

    for instruction_step_data in instruction_steps_data:
        description = instruction_step_data["instruction"]
        step_number = instruction_step_data["order"]
        image_urls = parse_image_urls(instruction_step_data["media"]["images"])

        instruction_steps.append(
            InstructionStep(
                step_number=step_number, description=description, image_urls=image_urls
            )
        )

    return instruction_steps
