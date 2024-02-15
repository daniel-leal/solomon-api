import openpyxl  # noqa
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from fastapi_pagination import Params
from starlette import status

from app.solomon.auth.application.security import get_current_user
from app.solomon.auth.presentation.models import (
    UserTokenAuthenticated,
)
from app.solomon.common.data_transformation import DataTransformationError
from app.solomon.common.exceptions import ExcelGenerationError
from app.solomon.transactions.application.dependencies import get_transaction_service
from app.solomon.transactions.application.services import TransactionService
from app.solomon.transactions.domain.exceptions import (
    NoTransactionsFound,
    TransactionNotFound,
)
from app.solomon.transactions.presentation.models import (
    PaginatedTransactionResponseMapper,
    TransactionCreate,
    TransactionFilters,
    TransactionResponseMapper,
)

transaction_router = APIRouter()


@transaction_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> TransactionResponseMapper:
    """
    Create a new transaction.

    This function receives a TransactionCreate object and a TransactionService instance,
    then tries to create a new transaction using the provided service.

    Parameters
    ----------
    transaction : TransactionCreate
        The transaction to be created.
    transaction_service : TransactionService, optional
        The service to be used to create the transaction, by default
        Depends(get_transaction_service)
    current_user: Logged in user

    Returns
    -------
    JSONResponse
        The created transaction with a 201 status code.
    """
    try:
        transaction = transaction.model_copy(update={"user_id": current_user.id})
        created_transaction = transaction_service.create_transaction(transaction)
        return created_transaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@transaction_router.get("/export")
async def export_transactions(
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
    filters: TransactionFilters = Depends(),
):
    try:
        excel_bytes = transaction_service.export_transactions(
            user_id=current_user.id, filters=filters
        )

        return StreamingResponse(
            excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", # noqa
            headers={"Content-Disposition": "attachment; filename=transactions.xlsx"},
        )
    except (
        NoTransactionsFound,
        DataTransformationError,
        ExcelGenerationError,
        Exception,
    ) as e:
        raise HTTPException(
            detail=f"An error occurred while exporting transactions: {e}",
            status_code=500,
        )


@transaction_router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> TransactionResponseMapper:
    """
    Retrieve a transaction by its ID.

    This function receives a transaction_id and a TransactionService instance,
    then tries to retrieve the transaction using the provided service.

    Parameters
    ----------
    transaction_id : str
        The ID of the transaction to be retrieved.
    transaction_service : TransactionService, optional
        The service to be used to retrieve the transaction, by default
        Depends(get_transaction_service)
    current_user : UserTokenAuthenticated, optional
        The current user, by default Depends(get_current_user)

    Returns
    -------
    Transaction
        The retrieved transaction.
    """
    try:
        return transaction_service.get_transaction(transaction_id, current_user.id)
    except TransactionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@transaction_router.get("/")
async def get_transactions(
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
    pagination: Params = Depends(),
    filters: TransactionFilters = Depends(),
) -> PaginatedTransactionResponseMapper:
    """
    Retrieve all transactions.

    This function receives a TransactionService instance and a UserTokenAuthenticated
    instance, then tries to retrieve all transactions using the provided service.

    Parameters
    ----------
    transaction_service : TransactionService, optional
        The service to be used to retrieve the transactions, by default
        Depends(get_transaction_service)
    current_user : UserTokenAuthenticated, optional
        The current user, by default Depends(get_current_user)
    pagination: Params
        The pagination parameters
    filters: TransactionFilters
        The filters to be applied

    Returns
    -------
    PaginatedTransactionResponseMapper
        The retrieved transactions.
    """
    paginated_transactions = transaction_service.get_transactions(
        current_user.id, pagination, filters
    )

    return paginated_transactions
