"""Challenge and checkpoint API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin
from app.database.postgres import get_db
from app.schemas import (
    ApiResponse,
    Challenge,
    ChallengeCreate,
    Checkpoint,
    CheckpointCreate,
)
from app.services.challenge_service import ChallengeService


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
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
) -> ApiResponse[Challenge]:
    """Create a challenge."""

    service = ChallengeService(db)

    challenge = await service.create_challenge(
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
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
) -> ApiResponse[Checkpoint]:
    """Create a checkpoint."""

    service = ChallengeService(db)

    checkpoint = await service.create_checkpoint(
        payload,
    )

    return ApiResponse(
        message="Checkpoint created successfully",
        data=checkpoint,
    )