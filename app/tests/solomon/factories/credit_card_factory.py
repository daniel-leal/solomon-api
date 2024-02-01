from factory import Faker, SubFactory

from app.solomon.transactions.domain.models import CreditCard
from app.tests.solomon.factories.base_factory import BaseFactory
from app.tests.solomon.factories.user_factory import UserFactory


class CreditCardFactory(BaseFactory):
    class Meta:
        model = CreditCard

    name = Faker(
        "random_element", elements=["Itau", "Nubank", "Santander", "Banco do Brasil"]
    )
    limit = Faker("random_element", elements=[10000.00, 20000.00, 30000.00, 40000.00])
    invoice_start_day = Faker("random_element", elements=[7, 30, 15, 10])
    user = SubFactory(UserFactory)
