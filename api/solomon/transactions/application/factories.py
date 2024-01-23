from fastapi import Depends

from api.solomon.transactions.application.services import CreditCardService
from api.solomon.transactions.infrastructure.factories import get_credit_card_repository
from api.solomon.transactions.infrastructure.repositories import CreditCardRepository


def get_credit_card_service(
    credit_card_repository: CreditCardRepository = Depends(get_credit_card_repository),
) -> CreditCardService:
    """Factory for CreditCardService"""
    return CreditCardService(credit_card_repository)
