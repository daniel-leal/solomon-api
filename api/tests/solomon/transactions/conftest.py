from unittest.mock import Mock

import pytest

from api.solomon.transactions.application.services import CreditCardService


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def credit_card_service(mock_repository):
    return CreditCardService(credit_card_repository=mock_repository)
