from typing import List, TypeVar

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import desc

from app.solomon.infrastructure.database import CustomQuery
from app.solomon.transactions.domain.models import (
    Category,
    CreditCard,
    Installment,
    Transaction,
)

T = TypeVar("T")


class CategoryRepository:
    """Categories repository. It is used to interact with the database."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Category]:
        """Get all Credit Cards."""
        return self.session.query(Category).all()

    def get_by_id(self, id: str) -> Category | None:
        """Get a Credit Card by id."""
        return self.session.query(Category).filter_by(id=id).first()


class CreditCardRepository:
    """CreditCards repository. It is used to interact with the database."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self, user_id: str, **kwargs: dict) -> List[CreditCard]:
        """Get all Credit Cards."""
        return self.session.query(CreditCard).filter_by(user_id=user_id, **kwargs).all()

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

    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()

    def get_all(self, user_id: str, filters: dict) -> CustomQuery[Transaction]:
        """Get all transactions based on specified filters."""
        custom_query = CustomQuery(entities=Transaction, session=self.session)

        return (
            custom_query.filter(Transaction.user_id == user_id)
            .apply_filters(Transaction, filters)
            .order_by(desc(Transaction.date))
        )

    def get_by_id(self, transaction_id: str, user_id: str) -> Transaction | None:
        """Get a Transaction by id."""
        return (
            self.session.query(Transaction)
            .options(joinedload(Transaction.installments))
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

        return (
            self.session.query(Transaction)
            .options(joinedload(Transaction.installments))
            .filter_by(id=transaction.id)
            .first()
        )
