from sqlalchemy import Column, ForeignKey, Integer

from src.dev.config.base import Base


class ExitNoteDetail(Base):
    __tablename__ = "exit_note_detail"

    id = Column(Integer, primary_key=True)
    exit_id = Column(Integer, ForeignKey("exit_note.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
