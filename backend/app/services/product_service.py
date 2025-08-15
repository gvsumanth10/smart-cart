from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.product import Product

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """
    Retrieve a list of products from the database with pagination.
    """
    return db.query(Product).offset(skip).limit(limit).all()

def get_product_by_main_category(db: Session, main_category: str, skip: int = 0, limit: int = 100) -> List[Product]:
    """
    Retrieve products by main category with pagination.
    """
    return db.query(Product).filter(Product.main_category == main_category).offset(skip).limit(limit).all()

def get_product_by_sub_category(db: Session, sub_category: str, skip: int = 0, limit: int = 100) -> List[Product]:
    """
    Retrieve products by sub category with pagination.
    """
    return db.query(Product).filter(Product.sub_category == sub_category).offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """
    Retrieve a product by its ID.
    """
    return db.query(Product).filter(Product.id == product_id).first()

def search_products_by_name(db: Session, query: str) -> List[Product]:
    """
    Search for products by name.
    """
    search_terms = query.split()
    # Creae a filter condition for each term
    conditions = [Product.product_name.ilike(f"%{term}%") for term in search_terms]
    # Find products that match any of the search terms
    if conditions:
        return db.query(Product).filter(*conditions).all()
    # If no search terms, return all products
    else:
        return db.query(Product).filter(Product.product_name.ilike(f"%{query}%")).all()