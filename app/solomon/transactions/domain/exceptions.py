class CreditCardNotFound(Exception):
    """Credit Card not found exception."""

    pass


class CategoryNotFound(Exception):
    """Category not found exception."""

    pass


class TransactionNotFound(Exception):
    """Transaction not found exception."""

    pass


class NoTransactionsFound(Exception):
    """Transactions not found for filters"""

    pass
