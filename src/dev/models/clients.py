from sqlalchemy import Column, Integer, String
from src.dev.config.base import Base
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    phone = Column(String(20))
    address = Column(String(250))
