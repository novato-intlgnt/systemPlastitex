from sqlalchemy import Column, Integer, String

from src.dev.config.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20))
    address = Column(String(200))
