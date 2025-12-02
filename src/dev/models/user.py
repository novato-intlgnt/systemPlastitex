from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from src.dev.config.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    fullname = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)

    # Relaciones
    purchase_orders = relationship("PurchaseOrder", back_populates="user")
    entry_notes = relationship("EntryNote", back_populates="user")
    exit_notes = relationship("ExitNote", back_populates="user")
