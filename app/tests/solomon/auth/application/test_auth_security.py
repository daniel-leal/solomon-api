from unittest import mock

import pytest
from fastapi import HTTPException
from jwt import PyJWTError
from starlette.status import HTTP_401_UNAUTHORIZED

from app.solomon.auth.application.security import (
    generate_hashed_password,
    generate_token,
    get_current_user,
    is_password_valid,
    is_token_expired,
    verify_token,
)
from app.solomon.auth.domain.exceptions import ExpiredTokenError
from app.solomon.auth.presentation.models import UserTokenAuthenticated


def test_generate_hashed_password():
    password = "test_password"
    hashed_password = generate_hashed_password(password)
    assert hashed_password != password


def test_is_password_valid():
    password = "test_password"
    hashed_password = generate_hashed_password(password)
    assert is_password_valid(password, hashed_password) is True
    assert is_password_valid("wrong_password", hashed_password) is False


def test_generate_token():
    user_id = "test_user"
    token = generate_token(user_id)
    assert token is not None


def test_is_token_expired():
    user_id = "test_user"
    token = generate_token(user_id, expires_delta=1)
    payload = verify_token(token)
    assert is_token_expired(payload) is False


@mock.patch("jwt.decode")
def test_verify_token(mock_decode):
    mock_decode.return_value = {"sub": "test_user", "exp": 9999999999}
    token = "test_token"
    payload = verify_token(token)
    assert payload["sub"] == "test_user"


@mock.patch("jwt.decode")
def test_verify_token_expired(mock_decode):
    mock_decode.return_value = {"sub": "test_user", "exp": 0}
    token = "test_token"
    with pytest.raises(ExpiredTokenError):
        verify_token(token)


def test_verify_token_invalid():
    invalid_token = "invalid_token"
    with pytest.raises(PyJWTError):
        verify_token(invalid_token)


@pytest.mark.asyncio
@mock.patch("app.solomon.auth.application.security.verify_token")
@mock.patch("app.solomon.auth.application.security.get_user_repository")
async def test_get_current_user(mock_get_user_repository, mock_verify_token):
    mock_user_repository = mock.Mock()
    mock_get_user_repository.return_value = mock_user_repository
    mock_user_repository.get_by_id.return_value = mock.Mock(
        id="test_user", username="test_username", email="test_email"
    )
    mock_verify_token.return_value = {"sub": "test_user"}
    token = mock.Mock(credentials="test_token")

    user = await get_current_user(token, mock_user_repository)

    assert isinstance(user, UserTokenAuthenticated)
    assert user.id == "test_user"
    assert user.username == "test_username"
    assert user.email == "test_email"
    assert user.token == "test_token"


@pytest.mark.asyncio
@mock.patch("app.solomon.auth.application.security.verify_token")
@mock.patch("app.solomon.auth.application.security.get_user_repository")
async def test_get_current_user_not_found(mock_get_user_repository, mock_verify_token):
    mock_user_repository = mock.Mock()
    mock_get_user_repository.return_value = mock_user_repository
    mock_user_repository.get_by_id.return_value = None
    mock_verify_token.return_value = {"sub": "test_user"}
    token = mock.Mock(credentials="test_token")

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, mock_user_repository)

    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
@mock.patch("app.solomon.auth.application.security.verify_token")
@mock.patch("app.solomon.auth.application.security.get_user_repository")
async def test_get_current_user_invalid_token(
    mock_get_user_repository, mock_verify_token
):
    mock_verify_token.side_effect = ExpiredTokenError("Token has expired!")
    mock_user_repository = mock.Mock()
    mock_get_user_repository.return_value = mock_user_repository
    token = mock.Mock(credentials="test_token")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, mock_user_repository)
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Token has expired"


@pytest.mark.asyncio
@mock.patch("app.solomon.auth.application.security.verify_token")
@mock.patch("app.solomon.auth.application.security.get_user_repository")
async def test_get_current_user_invalid_pyjwt_token(
    mock_get_user_repository, mock_verify_token
):
    mock_verify_token.side_effect = PyJWTError("Invalid token")
    mock_user_repository = mock.Mock()
    mock_get_user_repository.return_value = mock_user_repository
    token = mock.Mock(credentials="test_token")

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, mock_user_repository)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"
