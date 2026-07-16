"""Level API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.core.auth import (
    get_current_admin,
    get_current_user,
)
from app.schemas import (
    ApiResponse,
    Level,
    LevelCreate,
)
from app.services import level_service


router = APIRouter(
    prefix="/levels",
    tags=["Levels"],
)


@router.get(
    "/{level_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get level",
    description=(
        "Return level details, checkpoints, challenges, "
        "and the authenticated user's progress."
    ),
)
async def get_level(
    level_id: str,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[dict]:
    """Return level details."""

    level = await level_service.get_level(
        level_id,
        current_user,
    )

    return ApiResponse(
        message="Level retrieved successfully",
        data=level,
    )


@router.post(
    "",
    response_model=ApiResponse[Level],
    status_code=status.HTTP_201_CREATED,
    summary="Create level",
    description="Create a new level. Admin access required.",
)
async def create_level(
    payload: LevelCreate,
    _admin: dict = Depends(get_current_admin),
) -> ApiResponse[Level]:
    """Create a new level."""

    level = await level_service.create_level(
        payload,
    )

    return ApiResponse(
        message="Level created successfully",
        data=level,
    )