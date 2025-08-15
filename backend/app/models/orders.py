from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .user import User
from .product import Product
# from app.db.base import Base
from datetime import datetime, timezone 
# from sqlalchemy.ext.declarative import declarative_base
from app.db.base import Base
# Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    order_status = Column(String, default="Pending")
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc), nullable=False)

    items = relationship("OrderItem", back_populates="order")
    user = relationship("User", back_populates="orders")

class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")

