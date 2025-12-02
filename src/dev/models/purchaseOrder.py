from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from src.dev.config.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    date = Column(TIMESTAMP)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relaciones
    user = relationship("User", back_populates="purchase_orders")
    supplier = relationship("Supplier", back_populates="purchase_orders")
    details = relationship("PurchaseOrderDetail", back_populates="order", cascade="all, delete-orphan")
