from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String

from src.dev.config.base import Base


class EntryNote(Base):
    __tablename__ = "entry_note"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    date = Column(TIMESTAMP)
    reference = Column(String(100))
