from datetime import date
from uuid import uuid4

import pandas as pd
import pytest

from app.solomon.common.data_transformation import DataTransformationError
from app.solomon.transactions.application.transforms import (
    ExportExcelTransformation,
)
from app.solomon.transactions.presentation.models import (
    TransactionsResponseMapper,
)
from app.tests.solomon.factories.category_factory import CategoryFactory
from app.tests.solomon.factories.credit_card_factory import CreditCardFactory
from app.tests.solomon.factories.transaction_factory import TransactionFactory


def test_transform_data():
    category = CategoryFactory.build()
    card = CreditCardFactory.build(name="Card A")

    transaction1 = TransactionFactory.build(
        category=category,
        category_id=category.id,
        date=None,
        recurring_day=5,
        amount=100.0,
        credit_card=card,
        credit_card_id=str(uuid4),
    )
    transaction2 = TransactionFactory.build(
        category=category,
        category_id=category.id,
        date=date(2024, 2, 11),
        recurring_day=None,
        amount=200.0,
        credit_card=None,
    )

    transactions = [transaction1, transaction2]
    raw_data = TransactionsResponseMapper.create(transactions)

    expected_df = pd.DataFrame(
        {
            "Descrição": [transaction1.description, transaction2.description],
            "Data": [None, date(2024, 2, 11)],
            "Recorrência": [5, None],
            "Categoria": [category.description, category.description],
            "Cartão": ["Card A", None],
            "Valor": [100.0, 200.0],
        },
    )

    result_df = ExportExcelTransformation.transform_data(raw_data)

    assert expected_df.equals(result_df)


def test_transform_data_failure():
    with pytest.raises(DataTransformationError):
        empty_dataframe = pd.DataFrame()
        ExportExcelTransformation.transform_data(empty_dataframe)
