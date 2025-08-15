from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import Product as ProductSchema
from app.services import product_service

router = APIRouter()

@router.get("/products/", response_model=List[ProductSchema])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of products from the database.
    """
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/products/category/{main_category}", response_model=List[ProductSchema])
def read_products_by_main_category(main_category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve products by main category.
    """
    products = product_service.get_product_by_main_category(db, main_category, skip, limit)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found for this main category")
    return products

@router.get("/products/{product_id}", response_model=ProductSchema)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a product by its ID.
    """
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.get("/products/sub-category/{sub_category}", response_model=List[ProductSchema])
def read_products_by_sub_category(sub_category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve products by sub category.
    """
    products = product_service.get_product_by_sub_category(db, sub_category, skip, limit)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found for this sub category")
    return products

@router.get("/products/search/", response_model=List[ProductSchema])
def search_products(query: str = Query(..., min_length=3), db: Session = Depends(get_db)):
    """
    Search for products by name.
    """
    products = product_service.search_products_by_name(db, query)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found matching the search criteria")
    return products
