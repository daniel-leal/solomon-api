from fastapi import Depends

from api.solomon.auth.application.security import generate_hashed_password
from api.solomon.auth.presentation.models import UserCreate, UserCreateResponse
from api.solomon.users.domain.exceptions import UserAlreadyExists
from api.solomon.users.infrastructure.factories import get_user_repository
from api.solomon.users.infrastructure.repositories import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user: UserCreate) -> UserCreateResponse:
        """
        Creates a new User

        Parameters
        ----------
        user : UserCreate
            UserCreate model with the user data

        Returns
        -------
        User
            User model with the user data
        """
        if self.user_repository.get_by_email(user.email):
            raise UserAlreadyExists(f"An user with email {user.email} already exists!")

        if self.user_repository.get_by_username(user.username):
            raise UserAlreadyExists(
                f"An user with username {user.username} already exists!"
            )

        hashed_password = generate_hashed_password(user.password)
        db_user = self.user_repository.create(
            username=user.username, email=user.email, hashed_password=hashed_password
        )
        return UserCreateResponse(username=db_user.username, email=db_user.email)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Factory for UserService"""
    return UserService(user_repository)
