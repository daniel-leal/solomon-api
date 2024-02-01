from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status

from app.solomon.transactions.application.dependencies import (
    get_category_service,
)
from app.solomon.transactions.application.services import (
    CategoryService,
)
from app.solomon.transactions.domain.exceptions import CategoryNotFound
from app.solomon.transactions.presentation.models import Category

category_router = APIRouter()


@category_router.get("/", response_model=List[Category])
async def get_all_categories(
    category_service: CategoryService = Depends(get_category_service),
) -> Response:
    """
    Get all categories.

    Parameters
    ----------
    category_service : CategoryService
        The service object to fetch categories.

    Returns
    -------
    Response
        The response object containing all categories.
    """
    return category_service.get_categories()


@category_router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: str,
    category_service: CategoryService = Depends(get_category_service),
) -> Response:
    """
    Get a category by id.

    Parameters
    ----------
    category_id : str
        The id of the category to retrieve.
    category_service : CategoryService
        The service object to fetch category.

    Returns
    -------
    Response
        The response object containing the category corresponding to the given id.

    Raises
    ------
    HTTPException
        If no category with the given id exists.
    """
    try:
        return category_service.get_category(id=category_id)
    except CategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
