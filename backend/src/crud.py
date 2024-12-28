from sqlmodel import Session, select
from .models import Recipe, Ingredient

def get_recipe_by_id(session: Session, recipe_id: int):
    return session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()

def update_recipes(session: Session, recipes_data: List[dict]):
    for data in recipes_data:
        recipe = Recipe(**data)
        session.add(recipe)
    session.commit() 