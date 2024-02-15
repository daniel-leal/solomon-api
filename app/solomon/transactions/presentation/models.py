import datetime
from typing import List, Optional, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    PositiveInt,
    field_validator,
    model_validator,
)

from app.solomon.common.models import PaginationMeta, ResponseMapper
from app.solomon.transactions.domain.models import (
    Category,
    CreditCard,
    Transaction,
)
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
    def create(cls, credit_card: CreditCard) -> Self:
        """
        Create a CreditCardMapper instance from a CreditCard object.

        Parameters
        ----------
        credit_card : CreditCard
            The CreditCard object to be mapped.

        Returns
        -------
        CreditCardMapper
            A CreditCardMapper instance representing the mapped CreditCard object.

        Notes
        -----
        This method creates a CreditCardMapper instance by mapping the attributes of
        the given CreditCard object. It performs validation based on the model
        configuration defined in the `model_config` attribute of the CreditCardMapper
        class.
        """
        return cls.model_validate(credit_card)


class CreditCardResponseMapper(ResponseMapper):
    """Response model for credit card"""

    @classmethod
    def create(cls, credit_card: CreditCard) -> Self:
        """
        Create a CreditCardResponseMapper instance.

        Parameters
        ----------
        credit_card : CreditCard
            The CreditCard object to be mapped.

        Returns
        -------
        CreditCardResponseMapper
            A CreditCardResponseMapper instance containing the mapped CreditCard
            object.

        Notes
        -----
        This method creates a CreditCardResponseMapper instance with the given
        CreditCard object mapped as its data attribute.
        """
        return cls(data=CreditCardMapper.create(credit_card))


class CreditCardsResponseMapper(ResponseMapper):
    """Response model for credit cards"""

    @classmethod
    def create(cls, credit_cards: List[CreditCard]) -> Self:
        """
        Create a CreditCardsResponseMapper instance.

        Parameters
        ----------
        credit_cards : List[CreditCard]
            List of CreditCard objects to be mapped.

        Returns
        -------
        CreditCardsResponseMapper
            A CreditCardsResponseMapper instance containing the mapped list of
            CreditCard objects.

        Notes
        -----
        This method creates a CreditCardsResponseMapper instance with the given list
        of CreditCard objects mapped as its data attribute.
        """
        return cls(
            data=[
                CreditCardMapper.create(credit_card)
                for credit_card in credit_cards
            ]
        )


class CategoryMapper(BaseModel):
    """Mapper model for categories"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    description: str

    @classmethod
    def create(cls, category: Category) -> Self:
        """
        Create a CategoryMapper instance from a Category object.

        Parameters
        ----------
        category : Category
            The Category object to be mapped.

        Returns
        -------
        CategoryMapper
            A CategoryMapper instance representing the mapped Category object.

        Notes
        -----
        This method creates a CategoryMapper instance by mapping the attributes of
        the given Category object. It performs validation based on the model
        configuration defined in the `model_config` attribute of the CategoryMapper
        class.
        """
        return cls.model_validate(category)


class CategoryResponseMapper(ResponseMapper):
    """Response model for categories"""

    @classmethod
    def create(cls, category: Category) -> Self:
        """
        Create a CategoryResponseMapper instance.

        Parameters
        ----------
        category : Category
            The Category object to be mapped.

        Returns
        -------
        CategoryResponseMapper
            A CategoryResponseMapper instance containing the mapped Category
            object.

        Notes
        -----
        This method creates a CategoryResponseMapper instance with the given Category
        object mapped as its data attribute.
        """
        return cls(data=CategoryMapper.create(category))


class CategoriesResponseMapper(ResponseMapper):
    """Response model for categories"""

    @classmethod
    def create(cls, categories: List[Category]) -> Self:
        """
        Create a CategoriesResponseMapper instance.

        Parameters
        ----------
        categories : List[Category]
            List of Category objects to be mapped.

        Returns
        -------
        CategoriesResponseMapper
            A CategoriesResponseMapper instance containing the mapped list of
            Category objects.

        Notes
        -----
        This method creates a CategoriesResponseMapper instance with the given list
        of Category objects mapped as its data attribute.
        """
        return cls(
            data=[CategoryMapper.create(category) for category in categories]
        )


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

    # Relationships
    credit_card: Optional[CreditCardMapper] = None
    category: Optional[CategoryMapper] = None


class TransactionCreate(TransactionBase):
    """Request model for creating a transaction"""

    installments_number: Optional[PositiveInt] = None

    @field_validator("recurring_day")
    @classmethod
    def validate_recurring_day(cls, recurring_day, values):
        is_fixed = values.data["is_fixed"]
        if is_fixed and recurring_day is None:
            raise ValueError(
                "recurring day is required when transaction is fixed"
            )
        return recurring_day

    @field_validator("date")
    @classmethod
    def validate_date(cls, date, values):
        is_fixed = values.data["is_fixed"]
        if not is_fixed and date is None:
            raise ValueError("date is required when transaction is not fixed")
        return date

    @model_validator(mode="before")
    @classmethod
    def validate_credit_card(cls, data):
        kind = data["kind"]
        credit_card_id = data.get("credit_card_id")
        if kind == Kinds.CREDIT and credit_card_id is None:
            raise ValueError(
                "credit card is required when transaction is credit"
            )
        elif kind != Kinds.CREDIT:
            data["credit_card_id"] = None
        return data


class TransactionMapper(TransactionBase):
    """Mapper model for transactions"""

    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: str
    installments: Optional[list[Installment]] = None

    @classmethod
    def create(cls, transaction: Transaction) -> Self:
        """
        Create a TransactionMapper instance from a Transaction object.

        Parameters
        ----------
        transaction : Transaction
            The Transaction object to be mapped.

        Returns
        -------
        TransactionMapper
            A TransactionMapper instance representing the mapped Transaction object.

        Notes
        -----
        This method creates a TransactionMapper instance by mapping the attributes of
        the given Transaction object. It performs validation based on the model
        configuration defined in the `model_config` attribute of the TransactionMapper
        class.

        The returned TransactionMapper instance may contain additional attributes based
        on the `model_config` specified for the TransactionMapper class.
        """
        return cls.model_validate(transaction)


class TransactionResponseMapper(ResponseMapper[TransactionMapper]):
    """Response model for transaction"""

    @classmethod
    def create(cls, transaction: Transaction):
        """
        Create a TransactionResponseMapper instance.

        Parameters
        ----------
        transaction : Transaction
            The Transaction object to be mapped.

        Returns
        -------
        TransactionResponseMapper
            A TransactionResponseMapper instance containing the mapped Transaction
            object.

        Notes
        -----
        This method creates a TransactionResponseMapper instance with the given
        Transaction object. It maps the Transaction object to a TransactionMapper object
        using the TransactionMapper.create method and stores it in the 'data' attribute
        of the TransactionResponseMapper instance.
        """
        return cls(data=TransactionMapper.create(transaction))


class TransactionsResponseMapper(ResponseMapper[List[TransactionMapper]]):
    """Response model for transactions"""

    @classmethod
    def create(cls, items: List[Transaction]) -> Self:
        """
        Create a TransactionsResponseMapper instance.

        Parameters
        ----------
        items : List[Transaction]
            List of Transaction objects to be mapped.

        Returns
        -------
        TransactionsResponseMapper
            A TransactionsResponseMapper instance containing mapped Transaction objects.

        Notes
        -----
        This method creates a TransactionsResponseMapper instance with the given list of
        Transaction objects. It maps each Transaction object to a TransactionMapper
        object using the TransactionMapper.create method and stores them in the 'data'
        attribute of the TransactionsResponseMapper instance.
        """
        return cls(
            data=[
                TransactionMapper.create(transaction) for transaction in items
            ]
        )


class PaginatedTransactionResponseMapper(
    ResponseMapper[List[TransactionMapper]]
):
    """Response model for paginated transactions"""

    @classmethod
    def create(
        cls,
        items: List[Transaction],
        page: int,
        pages: int,
        size: int,
        total: int,
    ):
        """
        Create a PaginatedTransactionResponseMapper instance.

        Parameters
        ----------
        items : List[Transaction]
            List of Transaction objects representing the items in the current page.
        page : int
            The current page number.
        pages : int
            The total number of pages.
        size : int
            The number of items per page.
        total : int
            The total number of items across all pages.

        Returns
        -------
        PaginatedTransactionResponseMapper
            A PaginatedTransactionResponseMapper instance representing the paginated
            response.

        Notes
        -----
        This method creates a PaginatedTransactionResponseMapper instance with the given
        parameters, including a list of Transaction objects representing the items in
        the current page, pagination metadata such as page number, total pages, page
        size, and total number of items.
        """
        return cls(
            data=TransactionsResponseMapper.create(items).data,
            meta=PaginationMeta(page=page, pages=pages, size=size, total=total),
        )


class TransactionFilters(BaseModel):
    date__gt: Optional[datetime.date] = None
    date__lt: Optional[datetime.date] = None
    category_id__eq: Optional[str] = None
    kind__eq: Optional[str] = None
    is_fixed__eq: Optional[bool] = None
    is_revenue__eq: Optional[bool] = None
