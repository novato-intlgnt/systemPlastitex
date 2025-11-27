from sqlalchemy import Column, ForeignKey, Integer

from src.dev.config.base import Base


class EntryNoteDetail(Base):
    __tablename__ = "entry_note_detail"

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("entry_note.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
