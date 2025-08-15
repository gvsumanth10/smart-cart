from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Float
# from sqlalchemy.ext.declarative import declarative_base
from app.db.base import Base
# Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    brand = Column(String)
    price = Column(Numeric(10, 2))
    original_price = Column(Numeric(10, 2))
    quantity = Column(String)
    rating = Column(Numeric(3, 1))
    stock_status = Column(String)
    product_url = Column(String, unique=True)
    image_url = Column(String)
    main_category = Column(String)
    sub_category = Column(String)
    sub_category_image_url = Column(String)