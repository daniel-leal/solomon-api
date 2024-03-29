"""Database Infrastructure Module"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import uuid4

from fastapi import Depends
from fastapi_pagination.bases import AbstractParams
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_sqlalchemy import db
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query, Session, declarative_base

from app.solomon.common.models import PaginatedResponse

Base = declarative_base()


T = TypeVar("T")


class CustomQuery(Query, Generic[T]):
    OPERATORS = {
        "eq": lambda field, value: field == value,
        "in": lambda field, value: field.in_(value),
        "like": lambda field, value: field.like(value),
        "ilike": lambda field, value: field.ilike(value),
        "gt": lambda field, value: field > value,
        "lt": lambda field, value: field < value,
        "gte": lambda field, value: field >= value,
        "lte": lambda field, value: field <= value,
    }

    def all(self) -> List[T]:
        return super().all()

    def apply_filters(
        self, model: T, filters: Dict[str, Any]
    ) -> "CustomQuery[T]":
        """
        Apply filters to the given model based on the provided dictionary of filters.

        Parameters
        ----------
        model : T
            The model to which filters will be applied.
        filters : dict
            A dictionary containing filters to be applied. Each key represents an
            attribute of the model, and the corresponding value is the condition to
            filter on that attribute.

        Returns
        -------
        CustomQuery[T]
            A CustomQuery instance representing the filtered result.

        Raises
        ------
        ValueError
            If an invalid operator is provided for a field or if no operator is
            specified for a field.

        Notes
        -----
        This method applies filters to the model based on the given dictionary. Each
        filter is specified in the form of '<field>__<operator>', where <field> is the
        attribute of the model and <operator> is the comparison operator. Supported
        comparison operators include 'eq' (equal), 'neq' (not equal),
        'gt' (greater than), 'lt' (less than), 'gte' (greater than or equal), and
        'lte' (less than or equal).
        """
        for attribute, value in filters.items():
            if "__" in attribute:
                field_name, operator_name = attribute.split("__")
                operator = self.OPERATORS[operator_name]
                if operator is None:
                    raise ValueError(
                        f"Invalid operator '{operator_name}' for field '{field_name}'"
                    )
            else:
                raise ValueError(
                    f"No operator specified for field '{attribute}'"
                )

            field = getattr(model, field_name)
            operator_func = operator(field, value)
            self = self.filter(operator_func)

        return self

    def paginate(
        self, params: Optional[AbstractParams]
    ) -> PaginatedResponse[T]:
        """
        Paginate the current query.

        Parameters
        ----------
        params : Optional[AbstractParams], optional
            Parameters for pagination (default is None).

        Returns
        -------
        PaginatedResponse[T]
            A PaginatedResponse instance representing the paginated results.

        Notes
        -----
        This method applies pagination to the current query using the provided
        parameters. It returns a PaginatedResponse instance containing the paginated
        results.

        If no parameters are provided, default pagination parameters may be used.
        """
        return paginate(self, params)


def get_db_session() -> Session:
    """Get the current database session."""
    return db.session


def get_repository(repo_class, session=None):
    """Return a dependency that provides a repository instance."""

    def _get_repo(session: Session = Depends(session or get_db_session)):
        return repo_class(session)

    return _get_repo


# noinspection PyMethodParameters
class BaseModel(Base):
    """Base model for all database models."""

    __abstract__ = True

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
