from factory import Faker

from app.solomon.transactions.domain.models import Category
from app.tests.solomon.factories.base_factory import BaseFactory


class CategoryFactory(BaseFactory):
    class Meta:
        model = Category

    description = Faker(
        "random_element", elements=["Alimentação", "Transporte", "Saúde"]
    )
