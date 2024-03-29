import datetime
from io import BytesIO
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi_pagination import Params

from app.solomon.common.data_transformation import DataTransformationError
from app.solomon.common.exceptions import ExcelGenerationError
from app.solomon.common.models import PaginatedResponse
from app.solomon.transactions.domain.exceptions import (
    CreditCardNotFound,
    NoTransactionsFound,
    TransactionNotFound,
)
from app.solomon.transactions.domain.models import Installment, Transaction
from app.solomon.transactions.domain.options import Kinds
from app.solomon.transactions.presentation.models import (
    PaginatedTransactionResponseMapper,
    TransactionFilters,
    TransactionsResponseMapper,
)
from app.tests.solomon.factories.category_factory import CategoryFactory
from app.tests.solomon.factories.credit_card_factory import CreditCardFactory
from app.tests.solomon.factories.installment_factory import (
    InstallmentCreateFactory,
)
from app.tests.solomon.factories.transaction_factory import (
    TransactionCreateFactory,
    TransactionFactory,
)


class TestCreditCardService:
    def test_get_credit_card(self, credit_card_service, mock_repository):
        mock_user_id = "123"
        credit_card = CreditCardFactory.build()
        mock_repository.get_by_id.return_value = credit_card

        result = credit_card_service.get_credit_card(
            "credit_card_id", mock_user_id
        )

        mock_repository.get_by_id.assert_called_once_with(
            credit_card_id="credit_card_id", user_id=mock_user_id
        )
        assert result == credit_card

    def test_get_invalid_credit_card(
        self, credit_card_service, mock_repository
    ):
        mock_user_id = "123"
        mock_repository.get_by_id.return_value = None

        with pytest.raises(CreditCardNotFound):
            credit_card_service.get_credit_card("invalid_id", mock_user_id)

            mock_repository.get_by_id.assert_called_once_with(
                id="invalid_id", user_id=mock_user_id
            )

    def test_get_credit_cards(self, credit_card_service, mock_repository):
        mock_user_id = "123"
        mock_credit_cards = [
            CreditCardFactory.build(),
            CreditCardFactory.build(),
        ]
        mock_repository.get_all.return_value = mock_credit_cards

        result = credit_card_service.get_credit_cards(mock_user_id)

        assert result == mock_credit_cards
        assert isinstance(result, list)
        assert len(result) == 2
        mock_repository.get_all.assert_called_once_with(user_id=mock_user_id)

    def test_create_credit_card(self, credit_card_service, mock_repository):
        mock_credit_card = CreditCardFactory.build()
        mock_repository.create.return_value = mock_credit_card

        result = credit_card_service.create_credit_card(
            user_id=mock_credit_card.user_id,
            name=mock_credit_card.name,
            limit=mock_credit_card.limit,
            invoice_start_day=mock_credit_card.invoice_start_day,
        )

        assert result == mock_credit_card
        mock_repository.create.assert_called_once_with(
            user_id=mock_credit_card.user_id,
            name=mock_credit_card.name,
            limit=mock_credit_card.limit,
            invoice_start_day=mock_credit_card.invoice_start_day,
        )

    def test_create_invalid_credit_card(
        self, credit_card_service, mock_repository
    ):
        mock_credit_card = CreditCardFactory.build()
        mock_repository.create.return_value = None

        result = credit_card_service.create_credit_card(
            user_id=mock_credit_card.user_id,
            name=mock_credit_card.name,
            limit=mock_credit_card.limit,
            invoice_start_day=mock_credit_card.invoice_start_day,
        )

        assert result is None
        mock_repository.create.assert_called_once_with(
            user_id=mock_credit_card.user_id,
            name=mock_credit_card.name,
            limit=mock_credit_card.limit,
            invoice_start_day=mock_credit_card.invoice_start_day,
        )

    def test_update_credit_card(self, credit_card_service, mock_repository):
        # Arrange
        mock_credit_card = CreditCardFactory.build()
        new_name = "New name"

        mock_repository.get_by_id.return_value = mock_credit_card
        mock_credit_card.name = new_name

        mock_repository.update.return_value = mock_credit_card

        # Act
        updated_credit_card = credit_card_service.update_credit_card(
            mock_credit_card, mock_credit_card.user_id, name=new_name
        )

        # Assert
        assert updated_credit_card.name == new_name
        mock_repository.update.assert_called_once_with(
            mock_credit_card, name=new_name
        )

    def test_update_credit_card_not_found(
        self, credit_card_service, mock_repository
    ):
        # Arrange
        mock_credit_card = CreditCardFactory.build()
        mock_credit_card.user_id = "test_user_id"
        mock_repository.get_by_id.return_value = None

        # Act and Assert
        with pytest.raises(CreditCardNotFound):
            credit_card_service.update_credit_card(
                mock_credit_card, mock_credit_card.user_id, name="New Name"
            )

    def test_delete_credit_card(self, credit_card_service, mock_repository):
        # Arrange
        mock_credit_card = CreditCardFactory.build()
        mock_credit_card.user_id = "test_user_id"
        mock_repository.get_by_id.return_value = mock_credit_card

        # Act
        deleted_credit_card = credit_card_service.delete_credit_card(
            mock_credit_card.id, mock_credit_card.user_id
        )

        # Assert
        assert deleted_credit_card == mock_credit_card
        mock_repository.delete.assert_called_once_with(
            credit_card=mock_credit_card
        )

    def test_delete_credit_card_not_found(
        self, credit_card_service, mock_repository
    ):
        # Arrange
        mock_credit_card = CreditCardFactory.build()
        mock_credit_card.user_id = "test_user_id"
        mock_repository.get_by_id.return_value = None

        # Act and Assert
        with pytest.raises(CreditCardNotFound):
            credit_card_service.delete_credit_card(
                mock_credit_card.id, mock_credit_card.user_id
            )


class TestTransactionService:
    @pytest.mark.parametrize(
        "kind",
        [
            Kinds.PIX.value,
            Kinds.DEBIT.value,
            Kinds.CASH.value,
            Kinds.TRANSFER.value,
        ],
    )
    def test_create_recurrent_transaction(
        self, kind, transaction_service, mock_repository
    ):
        # Arrange
        mock_transaction_create = TransactionCreateFactory.build(
            kind=kind, is_fixed=True, date=None, recurring_day=4
        )
        mock_repository.create.return_value = Transaction(
            id=str(uuid4()),
            description=mock_transaction_create.description,
            amount=mock_transaction_create.amount,
            date=mock_transaction_create.date,
            is_fixed=mock_transaction_create.is_fixed,
            is_revenue=mock_transaction_create.is_revenue,
            kind=mock_transaction_create.kind,
            category_id=mock_transaction_create.category_id,
            user_id=mock_transaction_create.user_id,
            recurring_day=mock_transaction_create.recurring_day,
        )

        # Act
        created_transaction = transaction_service.create_transaction(
            mock_transaction_create
        ).data

        # Assert
        assert created_transaction.is_fixed is True
        assert created_transaction.recurring_day == 4
        assert created_transaction.date is None
        assert created_transaction.kind == kind
        assert created_transaction.user_id == mock_transaction_create.user_id
        assert created_transaction.installments == []

    def test_create_credit_card_recurrent_transaction(
        self, transaction_service, mock_repository
    ):
        # Arrange
        mock_transaction_create = TransactionCreateFactory.build(
            kind=Kinds.CREDIT.value,
            is_fixed=True,
            date=None,
            recurring_day=4,
            credit_card_id=str(uuid4()),
        )

        mock_repository.create.return_value = Transaction(
            id=str(uuid4()),
            description=mock_transaction_create.description,
            amount=mock_transaction_create.amount,
            date=mock_transaction_create.date,
            is_fixed=mock_transaction_create.is_fixed,
            is_revenue=mock_transaction_create.is_revenue,
            kind=mock_transaction_create.kind,
            category_id=mock_transaction_create.category_id,
            user_id=mock_transaction_create.user_id,
            recurring_day=mock_transaction_create.recurring_day,
        )

        # Act
        created_transaction = transaction_service.create_transaction(
            mock_transaction_create
        ).data

        # Assert
        assert created_transaction.is_fixed is True
        assert created_transaction.recurring_day == 4
        assert created_transaction.date is None
        assert created_transaction.kind == Kinds.CREDIT.value
        assert created_transaction.user_id == mock_transaction_create.user_id
        assert created_transaction.installments == []

    def test_create_credit_card_variable_transaction(
        self, transaction_service, mock_repository
    ):
        # Arrange
        mock_transaction_create = TransactionCreateFactory.build(
            kind=Kinds.CREDIT.value,
            is_fixed=False,
            recurring_day=None,
            credit_card_id=str(uuid4()),
            installments_number=3,
        )

        mock_installments_create = [
            InstallmentCreateFactory.build(date="2023-12-24", amount=100.25),
            InstallmentCreateFactory.build(date="2024-01-24", amount=100.25),
            InstallmentCreateFactory.build(date="2024-02-24", amount=100.25),
        ]

        mock_repository.create_with_installments.return_value = Transaction(
            id=str(uuid4()),
            description=mock_transaction_create.description,
            amount=mock_transaction_create.amount,
            date=mock_transaction_create.date,
            is_fixed=mock_transaction_create.is_fixed,
            is_revenue=mock_transaction_create.is_revenue,
            kind=mock_transaction_create.kind,
            category_id=mock_transaction_create.category_id,
            user_id=mock_transaction_create.user_id,
            recurring_day=mock_transaction_create.recurring_day,
            installments=[
                Installment(**installment.model_dump(), id=str(uuid4()))
                for installment in mock_installments_create
            ],
        )

        # Act
        created_transaction = transaction_service.create_transaction(
            mock_transaction_create
        ).data
        installments = created_transaction.installments

        # Assert
        assert created_transaction.is_fixed is False
        assert created_transaction.recurring_day is None
        assert created_transaction.date is mock_transaction_create.date
        assert created_transaction.kind == Kinds.CREDIT.value
        assert created_transaction.user_id == mock_transaction_create.user_id

        # Assert installments
        assert len(installments) == 3
        assert installments[0].date == datetime.date(2023, 12, 24)
        assert installments[0].amount == 100.25
        assert installments[1].date == datetime.date(2024, 1, 24)
        assert installments[1].amount == 100.25
        assert installments[2].date == datetime.date(2024, 2, 24)
        assert installments[2].amount == 100.25

    @pytest.mark.parametrize("kind", [kind for kind in Kinds])
    def test_create_invalid_recurrent_transaction(self, kind):
        with pytest.raises(ValueError):
            TransactionCreateFactory.build(
                kind=kind, is_fixed=True, date="2024-01-15", recurring_day=None
            )

    def test_create_invalid_variable_transaction(self):
        with pytest.raises(ValueError):
            TransactionCreateFactory.build(
                kind=Kinds.CREDIT.value,
                is_fixed=False,
                recurring_day=None,
                installments_number=None,
                date=None,
                credit_card_id=str(uuid4()),
            )

    def test_create_credit_card_invalid_card_transaction(self):
        with pytest.raises(ValueError):
            TransactionCreateFactory.build(
                kind=Kinds.CREDIT.value,
                is_fixed=False,
                recurring_day=None,
                installments_number=None,
                date="2024-01-15",
            )

    def test_get_transaction(self, transaction_service, mock_repository):
        mock_user_id = "123"
        category = CategoryFactory.build()
        transaction = TransactionFactory.build(
            id=str(uuid4()),
            kind=Kinds.DEBIT.value,
            is_fixed=False,
            recurring_day=None,
            credit_card_id=str(uuid4()),
            category=category,
            category_id=category.id,
        )

        mock_repository.get_by_id.return_value = transaction

        result = transaction_service.get_transaction(
            "transaction_id", mock_user_id
        )

        mock_repository.get_by_id.assert_called_once_with(
            transaction_id="transaction_id", user_id=mock_user_id
        )

        assert result.data.id == transaction.id
        assert result.data.kind == transaction.kind
        assert result.data.is_fixed == transaction.is_fixed
        assert result.data.credit_card_id == transaction.credit_card_id
        assert result.data.recurring_day == transaction.recurring_day

    def test_get_invalid_transaction(
        self, transaction_service, mock_repository
    ):
        mock_user_id = "123"
        mock_repository.get_by_id.return_value = None

        with pytest.raises(TransactionNotFound):
            transaction_service.get_transaction("invalid_id", mock_user_id)

            mock_repository.get_by_id.assert_called_once_with(
                id="invalid_id", user_id=mock_user_id
            )

    def test_get_transactions(self, transaction_service, mock_repository):
        user_id = "123"
        pagination_params = Params(page=1, size=5)
        filters = TransactionFilters()
        mock_transactions = [
            TransactionFactory.build(id=str(uuid4), category_id=str(uuid4)),
            TransactionFactory.build(id=str(uuid4), category_id=str(uuid4)),
            TransactionFactory.build(id=str(uuid4), category_id=str(uuid4)),
        ]

        mock_repository.get_all.return_value.paginate.return_value = (
            PaginatedResponse(
                items=mock_transactions, page=1, pages=1, size=5, total=3
            )
        )

        expected_result = PaginatedTransactionResponseMapper.create(
            items=mock_transactions,
            page=1,
            pages=1,
            size=5,
            total=3,
        )

        result = transaction_service.get_transactions(
            user_id, pagination_params, filters
        )

        assert result == expected_result
        mock_repository.get_all.return_value.paginate.assert_called_once_with(
            pagination_params
        )

    def test_export_transactions_with_no_transactions(
        self, transaction_service, mock_repository
    ):
        with pytest.raises(NoTransactionsFound):
            filters = TransactionFilters()
            mock_repository.get_all.return_value.all.return_value = []
            transaction_service.export_transactions(
                user_id=str(uuid4), filters=filters
            )

    @patch(
        "app.solomon.transactions.application.services.TransactionsResponseMapper"
    )
    def test_export_transactions_with_data_transformation_error(
        self,
        mock_transactions_response_mapper,
        transaction_service,
        mock_repository,
    ):
        with pytest.raises(DataTransformationError):
            mock_repository.get_all.return_value.all.return_value = (
                TransactionFactory.build_batch(2)
            )
            mock_transactions_response_mapper.create.return_value = (
                TransactionsResponseMapper(data=[])
            )

            transaction_service.export_transactions(
                user_id=str(uuid4), filters=TransactionFilters()
            )

    @patch("app.solomon.transactions.application.services.ExcelExporter")
    def test_export_transaction_with_excel_generation_error(
        self, mock_excel_exporter, transaction_service, mock_repository
    ):
        mock_repository.get_all.return_value.all.return_value = (
            TransactionFactory.build_batch(2)
        )
        mock_excel_exporter.export.side_effect = ExcelGenerationError(
            "An error occurred while generating file"
        )

        with pytest.raises(ExcelGenerationError):
            transaction_service.export_transactions(
                user_id=str(uuid4), filters=TransactionFilters()
            )

    def test_export_transaction_with_database_error(self, transaction_service):
        transaction_service.side_effect = Exception(
            "Could not connect to the database."
        )

        with pytest.raises(Exception):
            transaction_service.export_transactions(
                str(uuid4()), TransactionFilters()
            )

    def test_export_transaction_to_excel_with_success(
        self, transaction_service, mock_repository
    ):
        category = CategoryFactory.build()
        mock_repository.get_all.return_value.all.return_value = (
            TransactionFactory.build_batch(2, category=category)
        )

        result = transaction_service.export_transactions(
            user_id=str(uuid4()), filters=TransactionFilters()
        )

        assert isinstance(result, BytesIO)
