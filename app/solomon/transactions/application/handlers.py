import logging
from datetime import datetime
from typing import List

from dateutil.relativedelta import relativedelta

from app.solomon.transactions.domain.models import Installment, Transaction
from app.solomon.transactions.presentation.models import (
    InstallmentCreate,
    TransactionCreate,
)

logger = logging.getLogger(__name__)


class CreditCardTransactionHandler:
    """Credit card transaction handler. It is used to create a transaction and its installments."""

    def __init__(self, transaction_repository):
        self.transaction_repository = transaction_repository

    def process_transaction(self, transaction: TransactionCreate) -> Transaction:
        """
        Create a transaction and its installments

        If a transaction has installments, it will create the installments based on the
        number of installments and the transaction amount. The installments will be
        created with the same amount and with the same day of the month as the original
        transaction.

        Parameters
        ----------
        transaction : TransactionCreate
            Transaction to be created

        Returns
        -------
        Transaction
            Created transaction
        """
        try:
            installments = InstallmentHandler.generate_installments(transaction)
            transaction_model = self._map_transaction_to_domain(transaction)
            installments_models = self._map_installments_to_domain(installments)

            response = self.transaction_repository.create_with_installments(
                transaction=transaction_model, installments=installments_models
            )

            return response
        except Exception as e:
            self.transaction_repository.rollback()
            logger.error(e)
            raise

    def _map_transaction_to_domain(self, transaction: TransactionCreate) -> Transaction:
        return Transaction(
            **transaction.model_dump(exclude_none=True, exclude=["installments_number"])
        )

    def _map_installments_to_domain(
        self, installments: List[InstallmentCreate]
    ) -> List[Installment]:
        return [Installment(**installment.model_dump()) for installment in installments]


class InstallmentHandler:
    """Installment handler. It is used to generate installments for a transaction."""

    @classmethod
    def generate_installments(
        cls, transaction: TransactionCreate
    ) -> List[InstallmentCreate]:
        """
        Generate installments for a transaction.

        Parameters
        ----------
        transaction : TransactionCreate
            The transaction for which installments need to be generated.

        Returns
        -------
        List[InstallmentCreate]
            A list of InstallmentCreate objects representing the generated installments.
        """

        if not transaction.installments_number:
            transaction.installments_number = 1

        installments_amount = round(
            transaction.amount / transaction.installments_number, 2
        )

        installments_dates = cls._generate_installment_dates(
            transaction.date, transaction.installments_number
        )

        installments = [
            InstallmentCreate(
                amount=installments_amount,
                installment_number=i + 1,
                date=date,
            )
            for i, date in enumerate(installments_dates)
        ]

        return installments

    @classmethod
    def _generate_installment_dates(
        cls, start_date: datetime, num_installments: int
    ) -> List[datetime]:
        dates = [start_date]

        for _ in range(1, num_installments):
            next_month = dates[-1] + relativedelta(months=1)
            dates.append(next_month)

        return dates
