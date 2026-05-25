"""Application-specific exception hierarchy."""


class AppError(Exception):
    """Base exception for application errors."""


class ValidationError(AppError):
    """Raised when input validation fails."""


class AuthenticationError(AppError):
    """Raised when authentication fails."""


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
