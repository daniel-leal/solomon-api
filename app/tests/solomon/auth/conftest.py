from unittest.mock import Mock

import pytest

from app.solomon.auth.application.services import AuthService


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def mock_auth_service(mock_repository):
    return AuthService(mock_repository)
