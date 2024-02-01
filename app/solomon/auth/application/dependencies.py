from fastapi import Depends

from app.solomon.auth.application.services import AuthService
from app.solomon.infrastructure.database import get_repository
from app.solomon.users.infrastructure.repositories import UserRepository

get_user_repository = get_repository(UserRepository)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Factory for AuthService"""
    return AuthService(user_repository)
