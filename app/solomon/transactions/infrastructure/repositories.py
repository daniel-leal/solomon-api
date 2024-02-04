from typing import List

from fastapi_pagination import Params

from app.solomon.common.models import PaginatedResponse
from app.solomon.transactions.domain.models import (
    Category,
    CreditCard,
    Installment,
    Transaction,
)


class CategoryRepository:
    """Categories repository. It is used to interact with the database."""

    def __init__(self, session):
        self.session = session

    def get_all(self) -> List[Category]:
        """Get all Credit Cards."""
        return self.session.query(Category).all()

    def get_by_id(self, id: str) -> Category | None:
        """Get a Credit Card by id."""
        return self.session.query(Category).filter_by(id=id).first()


class CreditCardRepository:
    """CreditCards repository. It is used to interact with the database."""

    def __init__(self, session):
        self.session = session

    def get_all(self, user_id: str) -> List[CreditCard]:
        """Get all Credit Cards."""
        return self.session.query(CreditCard).filter_by(user_id=user_id).all()

    def get_by_id(self, id: str, user_id: str) -> CreditCard | None:
        """Get a Credit Card by id."""
        return (
            self.session.query(CreditCard)
            .filter(CreditCard.id == id, CreditCard.user_id == user_id)
            .first()
        )

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def create(self, **kwargs) -> CreditCard:
        """Create a new Credit Card."""
        instance = CreditCard(**kwargs)
        self.session.add(instance)
        self.commit()
        return instance

    def update(self, credit_card: CreditCard, **kwargs) -> CreditCard:
        """Update a Credit Card."""
        for key, value in kwargs.items():
            setattr(credit_card, key, value)
        self.commit()
        return credit_card

    def delete(self, credit_card: CreditCard) -> CreditCard:
        """Delete a Credit Card."""
        self.session.delete(credit_card)
        self.commit()
        return credit_card


class TransactionRepository:
    """Transactions repository. It is used to interact with the database."""

    def __init__(self, session):
        self.session = session

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()

    def get_all(self, user_id: str, params: Params = None) -> PaginatedResponse:
        """Get all transactions based on specified filters."""
        return (
            self.session.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .paginate(params)
        )

    def get_by_id(self, transaction_id: str, user_id: str) -> Transaction | None:
        """Get a Transaction by id."""
        return (
            self.session.query(Transaction)
            .filter(Transaction.id == transaction_id, Transaction.user_id == user_id)
            .first()
        )

    def create(self, **kwargs) -> Transaction:
        """Create a new Transaction."""
        instance = Transaction(**kwargs)
        self.session.add(instance)
        self.commit()
        return instance

    def create_with_installments(
        self, transaction: Transaction, installments: List[Installment]
    ) -> Transaction:
        """Create a new Transaction along with its associated Installments."""
        transaction.installments = installments

        self.session.add(transaction)
        self.session.commit()
        return transaction
