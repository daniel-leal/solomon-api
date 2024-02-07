import factory

from app.solomon.transactions.domain.models import Installment
from app.solomon.transactions.presentation.models import InstallmentCreate
from app.tests.solomon.factories.base_factory import BaseFactory


def incrementing_sequence(start=1):
    num = start
    while True:
        yield num
        num += 1


incrementing_numbers = incrementing_sequence()


class InstallmentCreateFactory(BaseFactory):
    class Meta:
        model = InstallmentCreate

    installment_number = factory.LazyAttribute(lambda x: next(incrementing_numbers))


class InstallmentFactory(BaseFactory):
    class Meta:
        model = Installment

    date = factory.Faker("date")
    amount = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    installment_number = factory.LazyAttribute(lambda x: next(incrementing_numbers))
