"""Challenge and checkpoint API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.core.auth import get_current_admin
from app.schemas import (
    ApiResponse,
    Challenge,
    ChallengeCreate,
    Checkpoint,
    CheckpointCreate,
)
from app.services import challenge_service


challenge_router = APIRouter(
    prefix="/challenges",
    tags=["Challenges"],
)


checkpoint_router = APIRouter(
    prefix="/checkpoints",
    tags=["Checkpoints"],
)


@challenge_router.post(
    "",
    response_model=ApiResponse[Challenge],
    status_code=status.HTTP_201_CREATED,
    summary="Create Challenge",
    description="Create a new coding challenge. Admin access required.",
)
async def create_challenge(
    payload: ChallengeCreate,
    _admin: dict = Depends(get_current_admin),
) -> ApiResponse[Challenge]:
    """Create a challenge."""

    challenge = await challenge_service.create_challenge(
        payload,
    )

    return ApiResponse(
        message="Challenge created successfully",
        data=challenge,
    )


@checkpoint_router.post(
    "",
    response_model=ApiResponse[Checkpoint],
    status_code=status.HTTP_201_CREATED,
    summary="Create Checkpoint",
    description="Create a new checkpoint. Admin access required.",
)
async def create_checkpoint(
    payload: CheckpointCreate,
    _admin: dict = Depends(get_current_admin),
) -> ApiResponse[Checkpoint]:
    """Create a checkpoint."""

    checkpoint = await challenge_service.create_checkpoint(
        payload,
    )

    return ApiResponse(
        message="Checkpoint created successfully",
        data=checkpoint,
    )