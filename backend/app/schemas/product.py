from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class ProductBase(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    brand: Optional[str] = Field(None, description="Brand of the product")
    price: Optional[float] = Field(None, description="Price of the product")
    original_price: Optional[float] = Field(None, description="Original Price of the product")
    quantity: Optional[str] = Field(None, description="Quantity of the product")
    rating: Optional[float] = Field(None, description="Rating of the product")
    stock_status: Optional[str] = Field(None, description="Stock status of the product")
    product_url: Optional[str] = Field(None, description="URL of the product page")
    image_url: Optional[str] = Field(None, description="URL of the product image")
    sub_category_image_url: Optional[str] = Field(None, description="URL of the sub-category image")

    # --- CORRECTED RATING VALIDATOR ---
    @field_validator("rating", mode="before")
    @classmethod
    def clean_rating(cls, value):
        if value and isinstance(value, str):
            # Use a safer regex to find the first number
            match = re.search(r'(\d\.\d|\d)', value)
            if match:
                return float(match.group(1))
        # If not a string or no number is found, return the original value
        # Pydantic will handle if it's a valid float or None
        return value

class Product(ProductBase):
    # This correctly maps MongoDB's '_id' to our 'product_id' field
    product_id: str = Field(..., description="Unique identifier for the product", alias='_id')
    
    main_category: str = Field(..., description="Main category of the product")
    sub_category: Optional[str] = Field(None, description="Sub-category of the product")

    # --- NEW VALIDATOR TO HANDLE MONGODB's ObjectId ---
    @field_validator('product_id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, value):
        # This function runs before any other validation and converts
        # the ObjectId type to a plain string.
        if value:
            return str(value)
        return value

    class Config:
        from_attributes = True
        populate_by_name = True # This is essential for the 'alias' to work