from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String

from src.dev.config.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)

    stock = Column(Integer, default=0)
    sale_price = Column(Numeric(10, 2), default=0)
    purchase_price = Column(Numeric(10, 2), default=0)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)
