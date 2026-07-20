"""Student progress API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.core.auth import get_current_user
from app.schemas import (
    ApiResponse,
    CompleteCheckpointRequest,
    CompleteLevelRequest,
    VideoProgressRequest,
)
from app.services import progress_service


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
):
    dashboard = await progress_service.get_dashboard(
        current_user,
    )

    print("Dashboard =", dashboard)

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
) -> ApiResponse[dict]:
    """Complete a checkpoint."""

    result = await progress_service.complete_checkpoint(
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
) -> ApiResponse[dict]:
    """Update video watch progress."""

    result = await progress_service.update_video_progress(
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
) -> ApiResponse[dict]:
    """Complete a level."""

    result = await progress_service.complete_level(
        body,
        current_user,
    )

    return ApiResponse(
        message="Level completed successfully",
        data=result,
    )