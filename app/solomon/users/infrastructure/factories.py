from app.solomon.infrastructure.database import get_repository
from app.solomon.users.infrastructure.repositories import UserRepository

get_user_repository = get_repository(UserRepository)
