from api.solomon.infrastructure.database import get_repository
from api.solomon.transactions.infrastructure.repositories import CreditCardRepository

get_credit_card_repository = get_repository(CreditCardRepository)
