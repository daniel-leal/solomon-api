from fastapi import APIRouter, FastAPI

from app.solomon.auth.presentation.resources import router as auth_router
from app.solomon.transactions.presentation.categories_resources import (
    category_router,
)
from app.solomon.transactions.presentation.credit_cards_resources import (
    credit_card_router,
)
from app.solomon.transactions.presentation.transactions_resources import (
    transaction_router,
)

router = APIRouter()


@router.get("/health", status_code=200)
def health_check() -> dict[str, str]:
    """Health check endpoint"""

    return {"status": "healthy"}


def init_routes(app: FastAPI) -> None:
    """
    Function to initialize all routes for the application.

    Parameters
    ----------
    app: FastAPI
        FastAPI application instance
    """
    app.include_router(router, tags=["health"])
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(
        credit_card_router, prefix="/credit-cards", tags=["credit-cards"]
    )
    app.include_router(
        category_router, prefix="/categories", tags=["categories"]
    )
    app.include_router(
        transaction_router, prefix="/transactions", tags=["transactions"]
    )
