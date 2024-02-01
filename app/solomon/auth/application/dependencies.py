from fastapi import Depends

from app.solomon.auth.application.services import AuthService
from app.solomon.users.infrastructure.factories import get_user_repository
from app.solomon.users.infrastructure.repositories import UserRepository


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Factory for AuthService"""
    return AuthService(user_repository)
