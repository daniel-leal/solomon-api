from factory import Faker, SubFactory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal

from app.solomon.transactions.domain.options import Kinds
from app.solomon.transactions.domain.models import Transaction
from app.solomon.transactions.presentation.models import TransactionCreate
from app.tests.solomon.factories.base_factory import BaseFactory
from app.tests.solomon.factories.category_factory import CategoryFactory
from app.tests.solomon.factories.user_factory import UserFactory


class TransactionCreateFactory(BaseFactory):
    class Meta:
        model = TransactionCreate

    description = FuzzyChoice(["iFood", "Uber", "Formosa", "Spotify"])
    amount = FuzzyDecimal(0.01, 1000.00, precision=2)
    date = Faker("date")
    is_fixed = False
    is_revenue = False
    recurring_day = None
    kind = FuzzyChoice(Kinds)
    category_id = Faker("uuid4")
    user_id = Faker("uuid4")


class TransactionFactory(BaseFactory):
    class Meta:
        model = Transaction

    description = FuzzyChoice(["iFood", "Uber", "Formosa", "Spotify"])
    amount = FuzzyDecimal(0.01, 1000.00, precision=2)
    date = Faker("date")
    is_fixed = False
    is_revenue = False
    recurring_day = None
    kind = FuzzyChoice(Kinds)
    category = SubFactory(CategoryFactory)
