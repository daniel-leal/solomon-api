from factory import Faker

from api.solomon.transactions.domain.models import Category
from api.tests.solomon.factories.base_factory import BaseFactory


class CategoryFactory(BaseFactory):
    class Meta:
        model = Category

    description = Faker(
        "random_element", elements=["Alimentação", "Transporte", "Saúde"]
    )
