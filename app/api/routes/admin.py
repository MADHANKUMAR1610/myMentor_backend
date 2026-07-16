"""Admin API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.core.auth import (
    get_current_admin,
    get_current_user,
)
from app.schemas import ApiResponse
from app.services import admin_service


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/stats",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get dashboard statistics",
    description="Return dashboard statistics for administrators.",
)
async def get_admin_stats(
    _admin: dict = Depends(get_current_admin),
) -> ApiResponse[dict]:
    """Return admin dashboard statistics."""

    stats = await admin_service.get_stats()

    return ApiResponse(
        message="Dashboard statistics retrieved successfully",
        data=stats,
    )


@router.get(
    "/students",
    response_model=ApiResponse[list[dict]],
    status_code=status.HTTP_200_OK,
    summary="Get students",
    description="Return all registered students with their progress.",
)
async def get_admin_students(
    _admin: dict = Depends(get_current_admin),
) -> ApiResponse[list[dict]]:
    """Return student administration data."""

    students = await admin_service.get_students()

    return ApiResponse(
        message="Students retrieved successfully",
        data=students,
    )


@router.get(
    "/leaderboard",
    response_model=ApiResponse[list[dict]],
    status_code=status.HTTP_200_OK,
    summary="Get leaderboard",
    description="Return the student XP leaderboard.",
)
async def get_leaderboard(
    _user: dict = Depends(get_current_user),
) -> ApiResponse[list[dict]]:
    """Return the student XP leaderboard."""

    leaderboard = await admin_service.get_leaderboard()

    return ApiResponse(
        message="Leaderboard retrieved successfully",
        data=leaderboard,
    )