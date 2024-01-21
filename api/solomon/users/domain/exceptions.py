class UserAlreadyExists(Exception):
    """Raised when the user already exists."""

    pass


class UserNotFound(Exception):
    """Raised when the user is not found."""

    pass
