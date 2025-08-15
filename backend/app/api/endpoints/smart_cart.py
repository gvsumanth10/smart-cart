from fastapi import APIRouter, HTTPException, status, Depends
from app.services import nlp_service, product_mapping_service
from app.schemas.smart_cart import DishRequest, Ingredient, MappingTestResponse
from typing import List


router = APIRouter()

@router.post("/generate-ingredients", response_model=list)
def generate_ingredients(request: DishRequest):
    """
    Generate a list of ingredients for a given dish using the Gemini API.
    """
    try:
        ingredients = nlp_service.get_ingredients_from_dish(request.dish_query)

        if ingredients is None:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Could not process the dish name. Please try again."
            )
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))
    
    return ingredients

@router.post("/test-mapping", response_model=MappingTestResponse)
def test_product_mapping(request: DishRequest):
    """
    TEST ENDPOINT: Takes a dish query, gets ingredients from the LLM,
    and returns the direct output of the product mapping service.
    """
    # Step 1: Get ingredients from the dish query

    try:
        generic_ingredients = nlp_service.get_ingredients_from_dish(request.dish_query)
        if not generic_ingredients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No ingredients found for the provided dish query."
            )
        
        # Step 2: Pass the ingredients to the mapping service

        mapped_products, not_found_ingredients = product_mapping_service.map_ingredients_to_products(generic_ingredients)

        # Step 3: Return the response

        # return MappingTestResponse(
        #     matched_products=mapped_products,
        #     not_found_ingredients=not_found_ingredients
        # )
    
        return {"matched_products": mapped_products, "not_found_ingredients": not_found_ingredients}
    
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))