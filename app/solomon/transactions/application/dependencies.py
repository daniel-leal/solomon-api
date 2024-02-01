from fastapi import Depends

from app.solomon.infrastructure.database import get_repository
from app.solomon.transactions.application.services import (
    CategoryService,
    CreditCardService,
    TransactionService,
)
from app.solomon.transactions.infrastructure.repositories import (
    CategoryRepository,
    CreditCardRepository,
    TransactionRepository,
)

get_credit_card_repository = get_repository(CreditCardRepository)
get_category_repository = get_repository(CategoryRepository)
get_transaction_repository = get_repository(TransactionRepository)


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


def get_transaction_service(
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
) -> TransactionService:
    """Factory for TransactionService"""
    return TransactionService(transaction_repository)
