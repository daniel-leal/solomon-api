import factory

from api.solomon.users.domain.models import User
from api.tests.solomon.factories.base_factory import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    username = factory.Faker("user_name")
    hashed_password = factory.Faker("password")
