"""Application custom exceptions."""

from fastapi import status


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int,
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, message: str):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
        )


class BadRequestException(AppException):
    """Invalid request."""

    def __init__(self, message: str):
        super().__init__(
            message,
            status.HTTP_400_BAD_REQUEST,
        )


class UnauthorizedException(AppException):
    """Unauthorized request."""

    def __init__(self, message: str):
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    """Forbidden request."""

    def __init__(self, message: str):
        super().__init__(
            message,
            status.HTTP_403_FORBIDDEN,
        )