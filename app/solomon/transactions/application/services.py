from io import BytesIO
from typing import List

from fastapi_pagination import Params

from app.solomon.common.data_transformation import DataTransformationError
from app.solomon.common.exceptions import ExcelGenerationError
from app.solomon.common.file_exporter import ExcelExporter
from app.solomon.transactions.application.handlers import (
    CreditCardTransactionHandler,
)
from app.solomon.transactions.application.transforms import (
    ExportExcelTransformation,
)
from app.solomon.transactions.domain.exceptions import (
    CategoryNotFound,
    CreditCardNotFound,
    NoTransactionsFound,
    TransactionNotFound,
)
from app.solomon.transactions.domain.models import (
    CreditCard,
)
from app.solomon.transactions.domain.options import Kinds
from app.solomon.transactions.infrastructure.repositories import (
    CategoryRepository,
    CreditCardRepository,
    TransactionRepository,
)
from app.solomon.transactions.presentation.models import (
    CategoriesResponseMapper,
    CategoryResponseMapper,
    PaginatedTransactionResponseMapper,
    Transaction,
    TransactionCreate,
    TransactionFilters,
    TransactionResponseMapper,
    TransactionsResponseMapper,
)


class CreditCardService:
    """Service for handling CreditCard business logic."""

    def __init__(self, credit_card_repository: CreditCardRepository):
        self.credit_card_repository = credit_card_repository

    def get_credit_card(self, credit_card_id: str, user_id: str) -> CreditCard:
        """
        Retrieve a credit card by its ID.

        Parameters
        ----------
        credit_card_id : int
            The ID of the credit card to retrieve.
        user_id: str
            The ID of the user that owns the credit card.

        Returns
        -------
        CreditCard
            The retrieved credit card.
        """
        credit_card = self.credit_card_repository.get_by_id(
            credit_card_id=credit_card_id, user_id=user_id
        )

        if not credit_card:
            raise CreditCardNotFound("Credit card not found.")

        return credit_card

    def get_credit_cards(self, user_id: str) -> List[CreditCard]:
        """
        Retrieve all credit cards.

        Parameters
        ----------
        user_id : str
            The ID of the user that owns the credit cards.

        Returns
        -------
        List[CreditCard]
            A list of all credit cards.
        """
        return self.credit_card_repository.get_all(user_id=user_id)

    def create_credit_card(self, **kwargs) -> CreditCard:
        """
        Create a new credit card.

        Parameters
        ----------
        **kwargs:
            The credit card to be created.

        Returns
        -------
        CreditCard
            The created credit card.
        """
        return self.credit_card_repository.create(**kwargs)

    def update_credit_card(
        self, credit_card_id: str, user_id: str, **kwargs
    ) -> CreditCard:
        """
        Update a credit card.

        Parameters
        ----------
        credit_card_id : str
            The ID of the credit card to update.
        user_id: str
            The ID of the current user
        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        CreditCard
            The updated credit card.
        """
        credit_card = self.get_credit_card(credit_card_id, user_id)
        return self.credit_card_repository.update(credit_card, **kwargs)

    def delete_credit_card(
        self, credit_card_id: str, user_id: str
    ) -> CreditCard:
        """
        Delete a credit card by its ID.

        Parameters
        ----------
        credit_card_id : int
            The ID of the credit card to delete.
        user_id: str
            The ID of the user that owns the credit card.

        Returns
        -------
        CreditCard
        """
        credit_card = self.get_credit_card(credit_card_id, user_id)
        self.credit_card_repository.delete(credit_card=credit_card)
        return credit_card


class CategoryService:
    """Service for handling Category business logic."""

    def __init__(self, category_repository: CategoryRepository) -> None:
        self.category_repository = category_repository

    def get_categories(self) -> CategoriesResponseMapper:
        """
        Get all categories.

        Returns
        -------
        list of Category
            List of all categories.
        """
        categories = self.category_repository.get_all()
        return CategoriesResponseMapper.create(categories=categories)

    def get_category(self, category_id: str) -> CategoryResponseMapper:
        """Get a category by id."""
        category = self.category_repository.get_by_id(category_id)

        if not category:
            raise CategoryNotFound("Category not found.")

        return CategoryResponseMapper.create(category=category)


class TransactionService:
    """Transactions Services class"""

    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self.transaction_repository = transaction_repository

    def create_transaction(
        self, transaction: TransactionCreate
    ) -> TransactionResponseMapper:
        """
        Create a new transaction.

        Parameters
        ----------
        transaction : TransactionCreate
            The transaction data to create.

        Returns
        -------
        Transaction
            The created transaction.

        Raises
        ------
        ValueError
            If there are validation errors in the transaction data.
        Exception
            If any other error occurs.
        """
        created_transaction = self._handle_transaction(transaction)
        return TransactionResponseMapper.create(transaction=created_transaction)

    def get_transaction(
        self, transaction_id: str, user_id: str
    ) -> TransactionResponseMapper:
        """
        Retrieve a transaction by its ID and their installments if it has.

        Parameters
        ----------
        transaction_id : str
            The ID of the transaction to retrieve.
        user_id : str
            The ID of the user that owns the transactions.

        Returns
        -------
        Transaction
            The retrieved transaction.
        """
        transaction = self.transaction_repository.get_by_id(
            transaction_id=transaction_id, user_id=user_id
        )

        if not transaction:
            raise TransactionNotFound("Transaction not found.")

        return TransactionResponseMapper.create(transaction=transaction)

    def get_transactions(
        self,
        user_id: str,
        pagination_params: Params,
        filters: TransactionFilters,
    ) -> PaginatedTransactionResponseMapper:
        """
        Retrieve all transactions.

        Parameters
        ----------
        user_id : str
            The ID of the user that owns the transactions.
        pagination_params: Params
            The pagination parameters
        filters: TransactionFilters
            The filters to be applied to query

        Returns
        -------
        PaginatedTransactionResponseMapper
            A paginated list of filtered transactions.
        """
        paginated_transaction = self.transaction_repository.get_all(
            user_id=user_id, filters=filters.model_dump(exclude_none=True)
        ).paginate(pagination_params)

        return PaginatedTransactionResponseMapper.create(
            items=paginated_transaction.items,
            page=paginated_transaction.page,
            pages=paginated_transaction.pages,
            size=paginated_transaction.size,
            total=paginated_transaction.total,
        )

    def export_transactions(
        self, user_id: str, filters: TransactionFilters
    ) -> BytesIO:
        """
        Export transactions to an Excel file.

        Parameters
        ----------
            user_id: str
                The ID of the user whose transactions will be exported.
            filters: TransactionFilters (Optional)
                Filters to apply to the transactions.

        Returns
        -------
            bytes: The content of the exported Excel file.

        Raises
        ------
            NoTransactionsFound: If no transactions were found for the provided filters.
            DataTransformationError: If an error occurs during data transformation.
            ExcelGenerationError: If an error occurs during the generation of the Excel
            file.
            Exception: For any other unexpected errors.
        """
        try:
            filters_dict = filters.model_dump(exclude_none=True)

            transactions = self.transaction_repository.get_all(
                user_id=user_id, filters=filters_dict
            ).all()

            if not transactions:
                raise NoTransactionsFound(
                    "No transactions were found for this filters!"
                )

            transactions_mapper = TransactionsResponseMapper.create(
                items=transactions
            )
            dataframe_transactions = ExportExcelTransformation.transform_data(
                transactions_mapper
            )

            excel_file = ExcelExporter.export(dataframe_transactions)
            return excel_file
        except (
            NoTransactionsFound,
            DataTransformationError,
            ExcelGenerationError,
        ) as e:
            raise e
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def _handle_transaction(
        self, transaction: TransactionCreate
    ) -> Transaction:
        if transaction.kind == Kinds.CREDIT and not transaction.is_fixed:
            handler = CreditCardTransactionHandler(self.transaction_repository)
            return handler.process_transaction(transaction)

        created_transaction = self.transaction_repository.create(
            **transaction.model_dump(exclude_none=True)
        )

        return created_transaction
