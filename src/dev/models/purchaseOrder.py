from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, Numeric, String

from src.dev.config.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    date = Column(TIMESTAMP)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")
