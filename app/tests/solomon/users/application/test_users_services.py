from unittest.mock import Mock

import pytest

from app.solomon.auth.presentation.models import UserCreate
from app.solomon.users.application.services import UserService
from app.solomon.users.domain.exceptions import UserAlreadyExists
from app.solomon.users.domain.models import User
from app.solomon.users.infrastructure.repositories import UserRepository


def test_create_user():
    # Arrange
    user_data = UserCreate(
        username="testuser", email="testuser@example.com", password="testpassword"
    )
    user_repository_mock = Mock(spec=UserRepository)
    user_repository_mock.get_by_email.return_value = None
    user_repository_mock.get_by_username.return_value = None
    user_repository_mock.create.return_value = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password="hashedpassword",
    )

    user_service = UserService(user_repository=user_repository_mock)

    # Act
    result = user_service.create_user(user_data)

    # Assert
    user_repository_mock.get_by_email.assert_called_once_with(user_data.email)
    user_repository_mock.get_by_username.assert_called_once_with(user_data.username)
    user_repository_mock.create.assert_called_once()
    assert result.username == user_data.username
    assert result.email == user_data.email


def test_create_user_already_exists():
    # Arrange
    user_data = UserCreate(
        username="testuser", email="testuser@example.com", password="testpassword"
    )
    user_repository_mock = Mock(spec=UserRepository)
    user_repository_mock.get_by_email.return_value = user_data
    user_repository_mock.get_by_username.return_value = user_data

    user_service = UserService(user_repository=user_repository_mock)

    # Act and Assert
    with pytest.raises(UserAlreadyExists):
        user_service.create_user(user_data)
