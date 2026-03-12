import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default="wheel")  # "wheel" | "custom"
    symbol = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="active")  # "active" | "completed"
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)

    trades = relationship("Trade", back_populates="campaign")
