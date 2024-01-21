import datetime
import time
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

from api.solomon.auth.domain.exceptions import ExpiredTokenError
from api.solomon.auth.presentation.models import UserTokenAuthenticated
from api.solomon.infrastructure.config import EXPIRES_AT, SECRET_KEY
from api.solomon.users.infrastructure.factories import get_user_repository
from api.solomon.users.infrastructure.repositories import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()


def generate_hashed_password(password: str) -> str:
    """
    Generate a hashed password from a plain text password.

    Parameters
    ----------
    password : str
        The plain text password.

    Returns
    -------
    str
        The hashed password.
    """
    return pwd_context.hash(password)


def is_password_valid(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Parameters
    ----------
    plain_password : str
        The plain text password.
    hashed_password : str
        The hashed password.

    Returns
    -------
    bool
        True if the password is valid, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(
    user_id: str,
    secret_key: str = SECRET_KEY,
    expires_delta: int = EXPIRES_AT,
) -> str:
    """
    Generates a JWT token

    Parameters
    ----------
    user_id : str
        User ID
    secret_key : str
        Secret key
    expires_delta : datetime.timedelta in seconds
        Expiration time

    Returns
    -------
    str
        JWT token
    """
    payload = {
        "sub": user_id,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_delta),
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return token


def is_token_expired(payload) -> bool:
    """
    Checks if a JWT token is expired

    Parameters
    ----------
    payload : dict
        JWT payload

    Returns
    -------
    bool
        True if token is expired, False otherwise
    """
    return payload["exp"] < time.time()


def verify_token(token: str, secret_key: str = SECRET_KEY) -> Any:
    """
    Validates a JWT token

    Parameters
    ----------
    token : str
        JWT token
    secret_key : str
        Secret key

    Returns
    -------
    Any
        Decoded payload if token is valid

    Raises
    ------
    PyJWTError, KeyError
        If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        if is_token_expired(payload):
            raise ExpiredTokenError("Token has expired!")

        return payload
    except (PyJWTError, KeyError):
        raise


async def get_current_user(
    token: str = Depends(security),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserTokenAuthenticated:
    """
    Authenticates a user based on the provided JWT token.

    Parameters
    ----------
    token : str
        JWT token

    Returns
    -------
    UserCreateResponse
        User object if token is valid (email and username)

    Raises
    ------
    HTTPException
        If the token is invalid or expired
    """
    try:
        payload = verify_token(token.credentials)
        user_id = payload["sub"]
        user = user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserTokenAuthenticated(
            id=str(user.id),
            username=user.username,
            email=user.email,
            token=token.credentials,
        )
    except ExpiredTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (PyJWTError, KeyError):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
