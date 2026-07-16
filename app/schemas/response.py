"""Common API response schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(
    BaseModel,
    Generic[T],
):
    """Standard API response."""

    success: bool = True
    message: str
    data: T | None = None