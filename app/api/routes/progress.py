"""Student progress API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database.postgres import get_db

from app.schemas import (
    ApiResponse,
    CompleteCheckpointRequest,
    CompleteLevelRequest,
    VideoProgressRequest,
)

from app.services.progress_service import ProgressService


router = APIRouter(
    prefix="/progress",
    tags=["Progress"],
)


@router.get(
    "/dashboard",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Student Dashboard",
    description="Return the authenticated student's dashboard.",
)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)

    dashboard = await service.get_dashboard(
        current_user,
    )

    return ApiResponse(
        message="Dashboard retrieved successfully",
        data=dashboard,
    )


@router.post(
    "/checkpoint",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Complete Checkpoint",
    description="Mark a checkpoint as completed.",
)
async def complete_checkpoint(
    body: CompleteCheckpointRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:

    service = ProgressService(db)

    result = await service.complete_checkpoint(
        body,
        current_user,
    )

    return ApiResponse(
        message="Checkpoint completed successfully",
        data=result,
    )


@router.post(
    "/video",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Update Video Progress",
    description="Update watched video progress.",
)
async def update_video_progress(
    body: VideoProgressRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:

    service = ProgressService(db)

    result = await service.update_video_progress(
        body,
        current_user,
    )

    return ApiResponse(
        message="Video progress updated successfully",
        data=result,
    )


@router.post(
    "/complete-level",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Complete Level",
    description="Mark a level as completed after validation.",
)
async def complete_level(
    body: CompleteLevelRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:

    service = ProgressService(db)

    result = await service.complete_level(
        body,
        current_user,
    )

    return ApiResponse(
        message="Level completed successfully",
        data=result,
    )