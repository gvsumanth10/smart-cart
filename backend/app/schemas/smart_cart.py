from pydantic import BaseModel
from typing import List
from .product import Product as ProductSchema


class DishRequest(BaseModel):
    dish_query: str

class Ingredient(BaseModel):
    ingredient_name: str
    quantity: str

class MappingTestResponse(BaseModel):
    matched_products: List[ProductSchema]
    not_found_ingredients: List[str]