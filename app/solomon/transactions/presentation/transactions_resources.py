from fastapi import Depends
from fastapi.responses import Response
from fastapi.routing import APIRouter
from starlette import status

from app.solomon.auth.application.security import get_current_user
from app.solomon.auth.presentation.models import (
    UserTokenAuthenticated,
)
from app.solomon.transactions.application.dependencies import get_transaction_service
from app.solomon.transactions.application.services import TransactionService
from app.solomon.transactions.presentation.models import (
    Transaction,
    TransactionCreate,
)

transaction_router = APIRouter()


@transaction_router.post(
    "/", response_model=Transaction, status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    transaction: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> Response:
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

    Returns
    -------
    JSONResponse
        The created transaction with a 201 status code.
    """
    try:
        transaction = transaction.model_copy(update={"user_id": current_user.id})
        return transaction_service.create_transaction(transaction)
    except Exception as e:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(e)
        )
