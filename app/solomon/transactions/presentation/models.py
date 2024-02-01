import datetime
from typing import List, Optional

from pydantic import BaseModel, PositiveInt, validator

from app.solomon.transactions.domain.options import Kinds


class CreditCardBase(BaseModel):
    """Base model for credit card"""

    name: str
    limit: float
    invoice_start_day: int


class CreditCardCreate(CreditCardBase):
    """Request model for credit card creation"""

    pass


class CreditCardUpdate(BaseModel):
    """Request model for credit card update"""

    name: Optional[str] = None
    limit: Optional[float] = None
    invoice_start_day: Optional[PositiveInt] = None


class CreditCard(CreditCardBase):
    """Credit card model"""

    id: str

    class Config:
        from_attributes = True


class Category(BaseModel):
    """Response model for categories"""

    id: str
    description: str

    class Config:
        from_attributes = True


class InstallmentBase(BaseModel):
    """Base model for installments"""

    installment_number: int
    date: datetime.date
    amount: float


class InstallmentCreate(InstallmentBase):
    """Request model for creating installments"""

    pass


class Installment(InstallmentBase):
    """Response model for installments"""

    id: str

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    """Base model for transactions"""

    description: str
    amount: float
    is_fixed: bool
    is_revenue: bool
    date: Optional[datetime.date] = None
    recurring_day: Optional[PositiveInt] = None
    kind: Kinds
    category_id: str
    user_id: Optional[str] = None
    credit_card_id: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Request model for creating a transaction"""

    installments_number: Optional[PositiveInt] = None

    @validator("recurring_day", always=True)
    def validate_recurring_day(cls, recurring_day, values):
        is_fixed = values.get("is_fixed")
        if is_fixed and recurring_day is None:
            raise ValueError("recurring day is required when transaction is fixed")
        return recurring_day

    @validator("date", always=True)
    def validate_date(cls, date, values):
        is_fixed = values.get("is_fixed")
        if not is_fixed and date is None:
            raise ValueError("date is required when transaction is not fixed")
        return date

    @validator("credit_card_id", always=True)
    def validate_credit_card(cls, credit_card_id, values):
        kind = values.get("kind")
        if kind == Kinds.CREDIT and credit_card_id is None:
            raise ValueError("credit card is required when transaction is credit")
        elif kind != Kinds.CREDIT:
            credit_card_id = None

        return credit_card_id


class Transaction(TransactionBase):
    """Response model for transactions"""

    id: str
    installments: Optional[List[Installment]] = None

    class Config:
        from_attributes = True
