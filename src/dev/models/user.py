from sqlalchemy import Column, Integer, String, Text

from src.dev.config.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    fullname = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
