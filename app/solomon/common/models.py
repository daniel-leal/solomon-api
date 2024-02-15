from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """
    Pagination metadata model

    This model represents the metadata of a paginated response.

    Parameters
    ----------
    page : int
        The current page number.
    pages : int
        The total number of pages.
    size : int
        The size of each page.
    total : int
        The total number of items.
    """

    page: int
    pages: int
    size: int
    total: int


class PaginatedResponse(PaginationMeta, Generic[T]):
    """Paginated Response"""

    items: List[T]


class ResponseMapper(BaseModel, Generic[T]):
    """Response Mapper"""

    data: Optional[T] = None
    meta: Optional[PaginationMeta] = None
