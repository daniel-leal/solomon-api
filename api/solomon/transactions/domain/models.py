from uuid import uuid4

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.solomon.infrastructure.database import BaseModel


class CreditCard(BaseModel):
    __tablename__ = "credit_cards"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, default=uuid4)
    user = relationship("User", back_populates="credit_cards")

    name = Column(String(50), nullable=False)
    limit = Column(Float, nullable=False)
    invoice_start_day = Column(Integer, nullable=False)
