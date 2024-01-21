from fastapi import Depends

from api.solomon.users.application.services import UserService
from api.solomon.users.infrastructure.factories import get_user_repository
from api.solomon.users.infrastructure.repositories import UserRepository


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Factory for UserService"""
    return UserService(user_repository)
