from fastapi import Depends

from api.solomon.transactions.application.services import (
    CategoryService,
    CreditCardService,
)
from api.solomon.transactions.infrastructure.factories import (
    get_category_repository,
    get_credit_card_repository,
)
from api.solomon.transactions.infrastructure.repositories import (
    CategoryRepository,
    CreditCardRepository,
)


def get_credit_card_service(
    credit_card_repository: CreditCardRepository = Depends(get_credit_card_repository),
) -> CreditCardService:
    """Factory for CreditCardService"""
    return CreditCardService(credit_card_repository)


def get_category_service(
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    """Factory for CreditCardService"""
    return CategoryService(category_repository)
