import logging
from typing import List

from app.solomon.transactions.application.handlers import CreditCardTransactionHandler
from app.solomon.transactions.domain.exceptions import (
    CategoryNotFound,
    CreditCardNotFound,
    TransactionNotFound,
)
from app.solomon.transactions.domain.models import (
    Category,
    CreditCard,
)
from app.solomon.transactions.domain.options import Kinds
from app.solomon.transactions.infrastructure.repositories import (
    CategoryRepository,
    CreditCardRepository,
    TransactionRepository,
)
from app.solomon.transactions.presentation.models import (
    Transaction,
    TransactionCreate,
)

logger = logging.getLogger(__name__)


class CreditCardService:
    """Service for handling CreditCard business logic."""

    def __init__(self, credit_card_repository: CreditCardRepository):
        self.credit_card_repository = credit_card_repository

    def get_credit_card(self, credit_card_id: str, user_id: str) -> CreditCard:
        """
        Retrieve a credit card by its ID.

        Parameters
        ----------
        credit_card_id : int
            The ID of the credit card to retrieve.
        user_id: str
            The ID of the user that owns the credit card.

        Returns
        -------
        CreditCard
            The retrieved credit card.
        """
        credit_card = self.credit_card_repository.get_by_id(
            id=credit_card_id, user_id=user_id
        )

        if not credit_card:
            raise CreditCardNotFound("Credit card not found.")

        return credit_card

    def get_credit_cards(self, user_id: str) -> List[CreditCard]:
        """
        Retrieve all credit cards.

        Parameters
        ----------
        user_id : str
            The ID of the user that owns the credit cards.

        Returns
        -------
        List[CreditCard]
            A list of all credit cards.
        """
        return self.credit_card_repository.get_all(user_id=user_id)

    def create_credit_card(self, **kwargs) -> CreditCard:
        """
        Create a new credit card.

        Parameters
        ----------
        credit_card : CreditCard
            The credit card to create.

        Returns
        -------
        CreditCard
            The created credit card.
        """
        return self.credit_card_repository.create(**kwargs)

    def update_credit_card(
        self, credit_card_id: str, user_id: str, **kwargs
    ) -> CreditCard:
        """
        Update a credit card.

        Parameters
        ----------
        id : int
            The ID of the credit card to update.
        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        CreditCard
            The updated credit card.
        """
        credit_card = self.get_credit_card(credit_card_id, user_id)
        return self.credit_card_repository.update(credit_card, **kwargs)

    def delete_credit_card(self, credit_card_id: str, user_id: str) -> CreditCard:
        """
        Delete a credit card by its ID.

        Parameters
        ----------
        credit_card_id : int
            The ID of the credit card to delete.
        user_id: str
            The ID of the user that owns the credit card.

        Returns
        -------
        CreditCard
        """
        credit_card = self.get_credit_card(credit_card_id, user_id)
        self.credit_card_repository.delete(credit_card=credit_card)
        return credit_card


class CategoryService:
    """Service for handling Category business logic."""

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def get_categories(self) -> List[Category]:
        """
        Get all categories.

        Returns
        -------
        list of Category
            List of all categories.
        """
        return self.category_repository.get_all()

    def get_category(self, id: str) -> Category:
        """Get a category by id."""
        category = self.category_repository.get_by_id(id)

        if not category:
            raise CategoryNotFound("Category not found.")

        return category


class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self.transaction_repository = transaction_repository

    def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        """
        Create a new transaction.

        Parameters
        ----------
        transaction : TransactionCreate
            The transaction data to create.

        Returns
        -------
        Transaction
            The created transaction.

        Raises
        ------
        ValueError
            If there are validation errors in the transaction data.
        Exception
            If any other error occurs.
        """
        created_transaction = self._handle_transaction(transaction)
        return created_transaction

    def get_transaction(self, transaction_id: str, user_id: str) -> Transaction:
        """
        Retrieve a transaction by its ID and their installments if it has.

        Parameters
        ----------
        transaction_id : str
            The ID of the transaction to retrieve.
        user_id : str
            The ID of the user that owns the transactions.

        Returns
        -------
        Transaction
            The retrieved transaction.
        """
        transaction = self.transaction_repository.get_by_id(
            transaction_id=transaction_id, user_id=user_id
        )

        if not transaction:
            raise TransactionNotFound("Transaction not found.")

        return transaction

    def _handle_transaction(self, transaction: TransactionCreate) -> Transaction:
        if transaction.kind == Kinds.CREDIT and not transaction.is_fixed:
            handler = CreditCardTransactionHandler(self.transaction_repository)
            return handler.process_transaction(transaction)

        created_transaction = self.transaction_repository.create(
            **transaction.model_dump(exclude_none=True)
        )

        response = Transaction.model_validate(created_transaction)

        return response
