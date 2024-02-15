import pandas as pd

from app.solomon.common.data_transformation import (
    DataTransformation,
    DataTransformationError,
)
from app.solomon.transactions.presentation.models import (
    TransactionsResponseMapper,
)


class ExportExcelTransformation(DataTransformation):
    """Excel file transformation class"""

    __COLUMNS = [
        "Descrição",
        "Data",
        "Recorrência",
        "Categoria",
        "Cartão",
        "Valor",
    ]

    @classmethod
    def transform_data(
        cls, raw_data: TransactionsResponseMapper
    ) -> pd.DataFrame:
        """
        Transform raw data into a pandas DataFrame.

        Parameters:
            cls: The class itself.
            raw_data (TransactionsResponseMapper): The raw data to be transformed.

        Returns:
            pd.DataFrame: The transformed data as a pandas DataFrame.

        Raises:
            DataTransformationError: If an error occurs during data transformation.
        """
        try:
            if not raw_data.data:
                raise DataTransformationError(
                    "No data provided for transformation"
                )

            data = []

            for transaction_mapper in raw_data.data:
                recurrency_day = (
                    transaction_mapper.recurring_day
                    if transaction_mapper.recurring_day
                    else None
                )
                category = (
                    transaction_mapper.category.description
                    if transaction_mapper.category
                    else None
                )
                card = (
                    transaction_mapper.credit_card.name
                    if transaction_mapper.credit_card
                    else None
                )

                transaction_data = {
                    "Descrição": transaction_mapper.description,
                    "Data": transaction_mapper.date,
                    "Recorrência": recurrency_day,
                    "Categoria": category,
                    "Cartão": card,
                    "Valor": transaction_mapper.amount,
                }
                data.append(transaction_data)

            df = pd.DataFrame(data, columns=cls.__COLUMNS)
            df = df.where(pd.notna(df), None)

            return df
        except Exception as e:
            raise DataTransformationError(
                f"An error occurred while transforming data: {e}"
            )
