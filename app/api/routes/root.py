"""Application root endpoints."""

from fastapi import (
    APIRouter,
    status,
)

from app.schemas import ApiResponse

router = APIRouter()


@router.get(
    "/",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="API Health Check",
    description="Verify that the Digipin Academy API is running.",
)
async def root() -> ApiResponse[dict]:
    """Return API health status."""

    return ApiResponse(
        message="API is running successfully",
        data={
            "service": "Digipin Academy API",
            "status": "ok",
            "version": "1.0.0",
        },
    )