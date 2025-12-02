from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.dev.config.base import Base


class EntryNoteDetail(Base):
    __tablename__ = "entry_note_detail"

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("entry_note.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relaciones
    entry_note = relationship("EntryNote", back_populates="details")
    product = relationship("Product", back_populates="entry_note_details")
