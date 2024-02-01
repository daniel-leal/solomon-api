from fastapi.security import HTTPBearer

from app.solomon.auth.application.security import (
    generate_token,
    is_password_valid,
)
from app.solomon.auth.domain.exceptions import AuthenticationError
from app.solomon.auth.presentation.models import (
    LoginCreate,
    UserLoggedinResponse,
)
from app.solomon.users.infrastructure.repositories import UserRepository

security = HTTPBearer()


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

        token = generate_token(user.id)

        return UserLoggedinResponse(
            user_id=user.id, access_token=token, token_type="bearer"
        )
