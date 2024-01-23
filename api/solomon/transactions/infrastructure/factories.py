from api.solomon.infrastructure.database import get_repository
from api.solomon.transactions.infrastructure.repositories import (
    CategoryRepository,
    CreditCardRepository,
)

get_credit_card_repository = get_repository(CreditCardRepository)
get_category_repository = get_repository(CategoryRepository)
