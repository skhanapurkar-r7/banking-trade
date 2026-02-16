"""Custom exception classes for the application."""

from typing import Any, Dict, Optional


class TradeStoreException(Exception):
    """Base exception for Trade Store application."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize exception with message and optional details.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class TradeNotFoundException(TradeStoreException):
    """Raised when a trade is not found."""

    pass


class TradeValidationException(TradeStoreException):
    """Raised when trade validation fails."""

    pass


class VersionConflictException(TradeStoreException):
    """Raised when trade version conflict occurs."""

    pass


class MaturityDateException(TradeStoreException):
    """Raised when maturity date validation fails."""

    pass
