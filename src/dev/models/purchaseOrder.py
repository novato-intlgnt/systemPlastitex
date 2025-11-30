from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, Numeric, String
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

    # relaciones 
    supplier = relationship("Supplier", foreign_keys=[supplier_id])
    details = relationship("PurchaseOrderDetail", back_populates="order")
