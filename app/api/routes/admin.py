from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.database.postgres import get_db
from app.schemas import ApiResponse
from app.services.admin_service import AdminService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    service = AdminService(db)

    stats = await service.get_stats()

    return ApiResponse(
        message="Statistics retrieved successfully",
        data=stats,
    )


@router.get("/students")
async def get_students(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    service = AdminService(db)

    students = await service.get_students()

    return ApiResponse(
        message="Students retrieved successfully",
        data=students,
    )


@router.get("/leaderboard")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    service = AdminService(db)

    leaderboard = await service.get_leaderboard()

    return ApiResponse(
        message="Leaderboard retrieved successfully",
        data=leaderboard,
    )