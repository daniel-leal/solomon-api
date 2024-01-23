from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from api.solomon.infrastructure.database import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    credit_cards = relationship("CreditCard", back_populates="user")
