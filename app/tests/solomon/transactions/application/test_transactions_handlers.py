import datetime
from uuid import uuid4

from app.solomon.transactions.domain.models import Installment, Transaction
from app.solomon.transactions.domain.options import Kinds
from app.tests.solomon.factories.transaction_factory import TransactionCreateFactory


class TestCreditCardTransactionHandlers:
    def test_process_transaction_success(self, transaction_handler, mock_repository):
        # Arrange
        mock_transaction_create = TransactionCreateFactory.build(
            kind=Kinds.CREDIT.value,
            is_fixed=False,
            recurring_day=None,
            credit_card_id=str(uuid4()),
            installments_number=3,
            amount=300,
            date="2023-12-20",
        )

        mock_repository.create_with_installments.return_value = Transaction(
            id=uuid4(),
            description=mock_transaction_create.description,
            amount=mock_transaction_create.amount,
            date=mock_transaction_create.date,
            recurring_day=mock_transaction_create.recurring_day,
            is_fixed=mock_transaction_create.is_fixed,
            is_revenue=mock_transaction_create.is_revenue,
            kind=mock_transaction_create.kind,
            user_id=mock_transaction_create.user_id,
            category_id=mock_transaction_create.category_id,
            credit_card_id=mock_transaction_create.credit_card_id,
            installments=[
                Installment(id=uuid4(), amount=100, date=datetime.date(2023, 12, 20)),
                Installment(id=uuid4(), amount=100, date=datetime.date(2024, 1, 20)),
                Installment(id=uuid4(), amount=100, date=datetime.date(2024, 2, 20)),
            ],
        )

        # Act
        result = transaction_handler.process_transaction(mock_transaction_create)

        # Assert
        assert result.id is not None
        assert result.description == mock_transaction_create.description
        assert result.amount == mock_transaction_create.amount
        assert result.date == mock_transaction_create.date
        assert result.recurring_day == mock_transaction_create.recurring_day
        assert result.is_fixed == mock_transaction_create.is_fixed
        assert result.is_revenue == mock_transaction_create.is_revenue
        assert result.kind == mock_transaction_create.kind
        assert result.user_id == mock_transaction_create.user_id
        assert result.category_id == mock_transaction_create.category_id
        assert result.credit_card_id == mock_transaction_create.credit_card_id
        assert len(result.installments) == 3

    def test_process_transaction_failure(self, transaction_handler, mock_repository):
        # Arrange
        mock_transaction_create = TransactionCreateFactory.build(
            kind=Kinds.CREDIT.value,
            is_fixed=False,
            recurring_day=None,
            credit_card_id=str(uuid4()),
            installments_number=3,
            amount=300,
            date="2023-12-20",
        )

        mock_repository.create_with_installments.side_effect = Exception(
            "Database not available"
        )

        # Act & Assert
        try:
            transaction_handler.process_transaction(mock_transaction_create)
            assert False, "Exception not raised"
        except Exception as e:
            assert str(e) == "Database not available"
            mock_repository.rollback.assert_called_once()


class TestInstallmentHandlers:
    def test_generate_installments(self, installment_handler):
        # Arrange
        transaction = TransactionCreateFactory.build(
            kind=Kinds.CREDIT.value,
            is_fixed=False,
            recurring_day=None,
            credit_card_id=str(uuid4()),
            installments_number=3,
            amount=300,
            date="2023-12-20",
        )

        # Act
        installments = installment_handler.generate_installments(transaction)

        # Assert
        assert len(installments) == 3
        assert installments[0].amount == 100
        assert installments[1].amount == 100
        assert installments[2].amount == 100

        assert installments[0].date == datetime.date(2023, 12, 20)
        assert installments[1].date == datetime.date(2024, 1, 20)
        assert installments[2].date == datetime.date(2024, 2, 20)

        assert installments[0].installment_number == 1
        assert installments[1].installment_number == 2
        assert installments[2].installment_number == 3

    def test_generate_installments_for_transaction_without_installments_number(
        self, installment_handler
    ):
        # Arrange
        transaction = TransactionCreateFactory.build(
            kind=Kinds.CREDIT.value,
            is_fixed=False,
            recurring_day=None,
            credit_card_id=str(uuid4()),
            installments_number=None,
            amount=300.15,
            date="2024-02-13",
        )

        # Act
        installments = installment_handler.generate_installments(transaction)

        # Assert
        assert len(installments) == 1
        assert installments[0].amount == 300.15
        assert installments[0].date == datetime.date(2024, 2, 13)
        assert installments[0].installment_number == 1
