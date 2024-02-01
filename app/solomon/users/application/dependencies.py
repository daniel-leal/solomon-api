from fastapi import Depends

from app.solomon.infrastructure.database import get_repository
from app.solomon.users.application.services import UserService
from app.solomon.users.infrastructure.repositories import UserRepository

get_user_repository = get_repository(UserRepository)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Factory for UserService"""
    return UserService(user_repository)
