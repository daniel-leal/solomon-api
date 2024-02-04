import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    PositiveInt,
    field_validator,
    model_validator,
)

from app.solomon.common.models import PaginationMeta, ResponseMapper
from app.solomon.transactions.domain.models import Category, CreditCard, Transaction
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


class CreditCardMapper(CreditCardBase):
    """Mapper model for credit card"""

    model_config = ConfigDict(from_attributes=True)

    id: str

    @classmethod
    def create(cls, credit_card: CreditCard):
        return cls.model_validate(credit_card)


class CreditCardResponseMapper(ResponseMapper):
    """Response model for credit card"""

    @classmethod
    def create(cls, credit_card: CreditCard):
        return cls(data=CreditCardMapper.create(credit_card))


class CreditCardsResponseMapper(ResponseMapper):
    """Response model for credit cards"""

    @classmethod
    def create(cls, credit_cards: List[CreditCard]):
        return cls(
            data=[CreditCardMapper.create(credit_card) for credit_card in credit_cards]
        )


class CategoryMapper(BaseModel):
    """Mapper model for categories"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    description: str

    @classmethod
    def create(cls, category: Category):
        return cls.model_validate(category)


class CategoryResponseMapper(ResponseMapper):
    """Response model for categories"""

    @classmethod
    def create(cls, category: Category):
        return cls(data=CategoryMapper.create(category))


class CategoriesResponseMapper(ResponseMapper):
    """Response model for categories"""

    @classmethod
    def create(cls, categories: List[Category]):
        return cls(data=[CategoryMapper.create(category) for category in categories])


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

    model_config = ConfigDict(from_attributes=True)

    id: str


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

    @field_validator("recurring_day")
    def validate_recurring_day(cls, recurring_day, values):
        is_fixed = values.data["is_fixed"]
        if is_fixed and recurring_day is None:
            raise ValueError("recurring day is required when transaction is fixed")
        return recurring_day

    @field_validator("date")
    def validate_date(cls, date, values):
        is_fixed = values.data["is_fixed"]
        if not is_fixed and date is None:
            raise ValueError("date is required when transaction is not fixed")
        return date

    @model_validator(mode="before")
    def validate_credit_card(cls, data):
        kind = data["kind"]
        credit_card_id = data.get("credit_card_id")
        if kind == Kinds.CREDIT and credit_card_id is None:
            raise ValueError("credit card is required when transaction is credit")
        elif kind != Kinds.CREDIT:
            credit_card_id = None
        return data


class TransactionMapper(TransactionBase):
    """Mapper model for transactions"""

    model_config = ConfigDict(
        from_attributes=True, extra="allow", arbritrary_types_allowed=True
    )

    id: str
    installments: Optional[list[Installment]] = None

    @classmethod
    def create(cls, transaction: Transaction):
        return cls.model_validate(transaction)


class TransactionResponseMapper(ResponseMapper):
    """Response model for transaction"""

    @classmethod
    def create(cls, transaction: Transaction):
        return cls(data=TransactionMapper.create(transaction))


class PaginatedTransactionResponseMapper(ResponseMapper):
    """Response model for paginated transactions"""

    @classmethod
    def create(
        cls, items: List[Transaction], page: int, pages: int, size: int, total: int
    ):
        return cls(
            data=[TransactionMapper.create(transaction) for transaction in items],
            meta=PaginationMeta(page=page, pages=pages, size=size, total=total),
        )
