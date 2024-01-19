import datetime

import jwt
from passlib.context import CryptContext

from api.solomon.infrastructure.config import EXPIRES_AT, SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
