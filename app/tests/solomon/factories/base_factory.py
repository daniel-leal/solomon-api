import factory
from fastapi_sqlalchemy import db
from sqlalchemy.orm import scoped_session

Session = scoped_session(
    lambda: db.session,
    scopefunc=lambda: db.session,
)


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base class for factories"""

    class Meta:
        """Base model for factories"""

        abstract = True
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"
