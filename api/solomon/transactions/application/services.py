from typing import List

from api.solomon.transactions.domain.exceptions import CreditCardNotFound
from api.solomon.transactions.domain.models import CreditCard
from api.solomon.transactions.infrastructure.repositories import (
    CreditCardRepository,
)


class CreditCardService:
    """CreditCards services"""

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
