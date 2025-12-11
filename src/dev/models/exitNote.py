from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from src.dev.config.base import Base


class ExitNote(Base):
    __tablename__ = "exit_note"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    date = Column(TIMESTAMP)
    total = Column(Numeric(10, 2), nullable=False)
    reference = Column(String(100))
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relaciones
    user = relationship("User")
    customer = relationship("Customer", foreign_keys=[customer_id])
    details = relationship("ExitNoteDetail", back_populates="exit_note")
