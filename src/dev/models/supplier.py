from sqlalchemy import Column, Integer, String

from src.dev.config.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20))
    address = Column(String(200))
