from typing import Optional
from uuid import uuid4

from fastapi import Depends
from fastapi_pagination.bases import AbstractParams
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_sqlalchemy import db
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query, Session, declarative_base

Base = declarative_base()


class CustomQuery(Query):
    def paginate(self, params: Optional[AbstractParams]):
        return paginate(self, params)


def get_db_session() -> Session:
    """Get the current database session."""
    return db.session


def get_repository(repo_class, session=None):
    """Return a dependency that provides a repository instance."""

    def _get_repo(session: Session = Depends(session or get_db_session)):
        return repo_class(session)

    return _get_repo


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
