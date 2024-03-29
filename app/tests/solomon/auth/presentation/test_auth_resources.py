from unittest.mock import Mock, patch

from app.solomon.auth.application.dependencies import get_auth_service
from app.solomon.auth.application.security import generate_hashed_password
from app.solomon.auth.domain.exceptions import ExpiredTokenError
from app.solomon.auth.presentation.models import UserCreate
from app.solomon.users.application.dependencies import get_user_service


def test_register_user(client):
    body = {
        "username": "John Doe",
        "email": "john.doe@example.com",
        "password": "123456",
    }

    response = client.post("/auth/register", json=body)

    assert response.status_code == 201
    assert response.json() == {
        "email": "john.doe@example.com",
        "username": "John Doe",
    }


def test_register_user_with_existing_username(client, user_factory):
    user = user_factory.create(username="John Doe")

    body = {
        "username": user.username,
        "email": "john.doe@example.com",
        "password": "123456",
    }

    response = client.post("/auth/register", json=body)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "An user with username John Doe already exists!"
    }


def test_register_user_with_existing_email(client, user_factory):
    user = user_factory.create(email="jhon.doe@example.com")

    body = {
        "username": "Jhon Doe",
        "email": user.email,
        "password": "123456",
    }

    response = client.post("/auth/register", json=body)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "An user with email jhon.doe@example.com already exists!"
    }


def test_authenticate_user(client, user_factory):
    password = "123456"
    user = user_factory.create(
        username="John Doe", hashed_password=generate_hashed_password(password)
    )

    body = {
        "username": user.username,
        "password": password,
    }

    response = client.post("/auth/login", json=body)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": response.json()["access_token"],
        "token_type": "bearer",
    }


def test_authenticate_user_with_invalid_username_or_password(
    client, user_factory
):
    password = "123456"
    user_factory.create(
        username="John Doe", hashed_password=generate_hashed_password(password)
    )

    body = {
        "username": "invalid_username",
        "password": "invalid_password",
    }

    response = client.post("/auth/login", json=body)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid username or password!",
    }


def test_register_exception(client):
    from app.solomon.main import app

    user = UserCreate(
        username="John Doe", email="jhon.doe@example.com", password="123456"
    )

    mock_user_service = Mock()
    mock_user_service.create_user = Mock(
        side_effect=Exception("Forced Exception")
    )

    app.dependency_overrides[get_user_service] = lambda: mock_user_service

    response = client.post("/auth/register", json=user.model_dump())

    assert response.status_code == 500
    assert response.json() == {"detail": "Forced Exception"}

    app.dependency_overrides = {}


def test_login_exception(client):
    from app.solomon.main import app

    user = UserCreate(
        username="John Doe", email="jhon.doe@example.com", password="123456"
    )

    mock_auth_service = Mock()
    mock_auth_service.authenticate = Mock(
        side_effect=Exception("Forced Exception")
    )

    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    response = client.post("/auth/login", json=user.model_dump())

    assert response.status_code == 500
    assert response.json() == {"detail": "Forced Exception"}

    app.dependency_overrides = {}


def test_get_current_user(client, user_factory):
    password = "123456"
    user = user_factory.create(
        username="John Doe", hashed_password=generate_hashed_password(password)
    )

    body = {
        "username": user.username,
        "password": password,
    }

    response = client.post("/auth/login", json=body)

    token = response.json()["access_token"]

    response = client.get(
        "/auth/profile", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "token": token,
    }


@patch("app.solomon.auth.application.security.verify_token")
def test_get_current_user_invalid_token(
    mock_verify_token, client, user_factory, mock_auth_service
):
    password = "123456"
    user = user_factory.create(
        username="John Doe", hashed_password=generate_hashed_password(password)
    )

    body = {
        "username": user.username,
        "password": password,
    }

    response = client.post("/auth/login", json=body)

    token = response.json()["access_token"]

    mock_verify_token.side_effect = ExpiredTokenError("Token has expired!")

    response = client.get(
        "/auth/profile", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired!"
