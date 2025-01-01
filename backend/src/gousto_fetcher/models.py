# dataclass models used only for parsing gousto api data
# Not reusing the sqlmodels for these due to extra complications with the link models

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ImageURL:
    url: str
    width: int


@dataclass
class Ingredient:
    name: str
    amount: str
    image_urls: List[ImageURL]


@dataclass
class InstructionStep:
    step_number: int
    description: str
    image_urls: List[ImageURL]


@dataclass
class Recipe:
    title: str
    gousto_uid: str
    images: List[ImageURL]
    rating: Optional[float]
    prep_time: int
    ingredients: List[Ingredient]
    instruction_steps: List[InstructionStep]
    basic_ingredients: List[str]
