from typing import Any, List, Optional

from pydantic import BaseModel


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


class PaginatedResponse(PaginationMeta):
    """Paginated Response"""

    items: List[Any]


class ResponseMapper(BaseModel):
    """Response Mapper"""

    data: Optional[Any] = None
    meta: Optional[PaginationMeta] = None
