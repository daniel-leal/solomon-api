import factory

from app.solomon.users.domain.models import User
from app.tests.solomon.factories.base_factory import BaseFactory


class UserFactory(BaseFactory):
    """User factory model"""

    class Meta:
        """User db model"""

        model = User

    email = factory.Faker("email")
    username = factory.Faker("user_name")
    hashed_password = factory.Faker("password")
