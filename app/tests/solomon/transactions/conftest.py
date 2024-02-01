from unittest.mock import Mock

import pytest

from app.solomon.transactions.application.handlers import (
    CreditCardTransactionHandler,
    InstallmentHandler,
)
from app.solomon.transactions.application.services import (
    CreditCardService,
    TransactionService,
)


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def credit_card_service(mock_repository):
    return CreditCardService(credit_card_repository=mock_repository)


@pytest.fixture
def transaction_service(mock_repository):
    return TransactionService(transaction_repository=mock_repository)


@pytest.fixture
def transaction_handler(mock_repository):
    return CreditCardTransactionHandler(transaction_repository=mock_repository)


@pytest.fixture
def installment_handler():
    return InstallmentHandler()
