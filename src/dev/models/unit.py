from sqlalchemy import Column, Integer, String

from src.dev.config.base import Base


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
