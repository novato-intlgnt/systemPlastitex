from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.dev.config.base import Base


class ExitNoteDetail(Base):
    __tablename__ = "exit_note_detail"

    id = Column(Integer, primary_key=True)
    exit_id = Column(Integer, ForeignKey("exit_note.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relaciones
    exit_note = relationship("ExitNote", back_populates="details")
    product = relationship("Product", back_populates="exit_note_details")
