class AuthenticationError(Exception):
    """Raised when the authentication fails."""

    pass


class ExpiredTokenError(Exception):
    """Raised when the token is expired."""

    pass
