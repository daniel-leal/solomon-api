from typing import List

from api.solomon.transactions.domain.models import CreditCard


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
