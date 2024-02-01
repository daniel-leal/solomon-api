from app.solomon.users.domain.models import User


class UserRepository:
    """User repository. It is used to interact with the database."""

    def __init__(self, session):
        self.session = session

    def get_by_id(self, id) -> User | None:
        """Get a user by id."""
        return self.session.query(User).filter_by(id=id).first()

    def get_by_email(self, email) -> User | None:
        """Get a user by email."""
        return self.session.query(User).filter_by(email=email).first()

    def get_by_username(self, username) -> User | None:
        """Get a user by username."""
        return self.session.query(User).filter_by(username=username).first()

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def create(self, **kwargs) -> User:
        """Create a new user."""
        instance = User(**kwargs)
        self.session.add(instance)
        self.commit()
        return instance
