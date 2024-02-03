from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.solomon.infrastructure.database import BaseModel


class CreditCard(BaseModel):
    """Credit card model"""

    __tablename__ = "credit_cards"

    user_id = Column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, default=uuid4
    )
    user = relationship("User", back_populates="credit_cards")

    name = Column(String(50), nullable=False)
    limit = Column(Float, nullable=False)
    invoice_start_day = Column(Integer, nullable=False)
    transactions = relationship("Transaction", back_populates="credit_card")


class Category(BaseModel):
    """Category model"""

    __tablename__ = "categories"

    description = Column(String(30), nullable=False)
    transactions = relationship("Transaction", back_populates="category")


class Transaction(BaseModel):
    """Transaction model"""

    __tablename__ = "transactions"

    description = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    is_fixed = Column(Boolean, nullable=False, default=False)
    is_revenue = Column(Boolean, nullable=False, default=False)
    date = Column(Date, nullable=True)
    recurring_day = Column(Integer, nullable=True)
    kind = Column(String(20), nullable=False)

    installments = relationship("Installment", back_populates="transaction")
    user = relationship("User", back_populates="transactions")
    credit_card = relationship("CreditCard", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    category_id = Column(UUID(as_uuid=False), ForeignKey("categories.id"))
    user_id = Column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, default=uuid4
    )
    credit_card_id = Column(
        UUID(as_uuid=False), ForeignKey("credit_cards.id"), nullable=True
    )


class Installment(BaseModel):
    """Installment model"""

    __tablename__ = "installments"

    date = Column(Date, nullable=False)
    installment_number = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)

    transaction_id = Column(
        UUID(as_uuid=False), ForeignKey("transactions.id"), nullable=False
    )
    transaction = relationship("Transaction", back_populates="installments")
