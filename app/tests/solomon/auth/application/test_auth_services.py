from unittest.mock import Mock

import pytest

from app.solomon.auth.application.security import generate_hashed_password
from app.solomon.auth.application.services import AuthService
from app.solomon.auth.domain.exceptions import AuthenticationError
from app.solomon.auth.presentation.models import LoginCreate, UserLoggedResponse
from app.solomon.users.infrastructure.repositories import UserRepository


def test_authenticate_success():
    # Arrange
    mock_user = Mock()
    mock_user.hashed_password = generate_hashed_password("valid_password")
    mock_user.id = 1

    mock_repo = Mock(UserRepository)
    mock_repo.get_by_username.return_value = mock_user

    auth_service = AuthService(mock_repo)
    login_create = LoginCreate(username="valid_username", password="valid_password")

    # Act
    result = auth_service.authenticate(login_create)

    # Assert
    assert isinstance(result, UserLoggedResponse)
    assert result.token_type == "bearer"


def test_authenticate_invalid_credentials():
    # Arrange
    mock_user = Mock()
    mock_user.hashed_password = generate_hashed_password("valid_password")
    mock_user.id = 1

    mock_repo = Mock(UserRepository)
    mock_repo.get_by_username.return_value = mock_user

    auth_service = AuthService(mock_repo)
    login_create = LoginCreate(username="valid_username", password="invalid_password")

    # Act and Assert
    with pytest.raises(AuthenticationError):
        auth_service.authenticate(login_create)
