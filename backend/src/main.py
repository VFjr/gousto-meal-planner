from fastapi import FastAPI, Depends
from sqlmodel import Session
from .database import get_session
from .crud import get_recipe_by_id, update_recipes
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/recipes/{recipe_id}")
async def read_recipe(recipe_id: int, session: Session = Depends(get_session)):
    return get_recipe_by_id(session, recipe_id)

@app.post("/recipes/")
async def update_recipe(recipes_data: List[dict], session: Session = Depends(get_session)):
    update_recipes(session, recipes_data)
    return {"message": "Recipes updated successfully"}