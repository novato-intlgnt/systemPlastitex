from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from src.dev.config.base import Base


class PurchaseOrderDetail(Base):
    __tablename__ = "purchase_order_detail"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("purchase_order.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relaciones
    order = relationship("PurchaseOrder", back_populates="details")
    product = relationship("Product", back_populates="purchase_order_details")
