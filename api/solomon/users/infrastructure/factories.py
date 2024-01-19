from api.solomon.infrastructure.database import get_repository
from api.solomon.users.infrastructure.repositories import UserRepository

get_user_repository = get_repository(UserRepository)
