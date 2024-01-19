from fastapi import Depends

from api.solomon.auth.domain.exceptions import AuthenticationError
from api.solomon.auth.presentation.models import LoginCreate, UserLoggedinResponse
from api.solomon.auth.utils import generate_token, is_password_valid
from api.solomon.users.infrastructure.factories import get_user_repository
from api.solomon.users.infrastructure.repositories import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate(self, login_create: LoginCreate) -> UserLoggedinResponse:
        """
        Authenticates a user and returns an access token

        Parameters
        ----------
        username : str
            Username
        password : str
            Password

        Returns
        -------
        UserLoggedinResponse
            Access token
        """
        user = self.user_repository.get_by_username(login_create.username)
        if not user or not is_password_valid(
            login_create.password, user.hashed_password
        ):
            raise AuthenticationError("Invalid username or password!")

        token = generate_token(str(user.id))

        return UserLoggedinResponse(access_token=token, token_type="bearer")


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Factory for AuthService"""
    return AuthService(user_repository)
