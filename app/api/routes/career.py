"""Career path API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database.postgres import get_db

from app.repositories.career_path_repository import (
    CareerPathRepository,
)

from app.schemas import (
    ApiResponse,
    CareerProfileCreate,
    CareerProfileResponse,
)

from app.services.career_path_service import (
    CareerPathService,
)

router = APIRouter(
    prefix="/career",
    tags=["Career Path"],
)


@router.post(
    "/profile",
    response_model=ApiResponse[CareerProfileResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create or Update Career Profile",
)
async def save_profile(
    payload: CareerProfileCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update the user's career profile."""

    repository = CareerPathRepository(db)

    service = CareerPathService(
        repository,
    )

    profile = await service.save_profile(
        payload,
        current_user,
    )

    return ApiResponse(
        message="Career profile saved successfully.",
        data=profile,
    )


@router.post(
    "/generate",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Generate Career Report",
    description="Generate an AI-powered career report and roadmap using Gemini.",
)
async def generate_career_report(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate career report."""

    repository = CareerPathRepository(db)

    service = CareerPathService(
        repository,
    )

    report = await service.generate_report(
        current_user,
    )

    return ApiResponse(
        message="Career report generated successfully.",
        data=report,
    )
@router.get(
    "/profile",
    response_model=ApiResponse[CareerProfileResponse],
    summary="Get Career Profile",
)
async def get_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    repository = CareerPathRepository(db)

    service = CareerPathService(
        repository,
    )

    profile = await service.get_profile(
        current_user,
    )

    return ApiResponse(
        message="Career profile fetched successfully.",
        data=profile,
    )
@router.get(
    "/report",
    response_model=ApiResponse[dict],
    summary="Get Career Report",
)
async def get_report(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    repository = CareerPathRepository(db)

    service = CareerPathService(
        repository,
    )

    report = await service.get_report(
        current_user,
    )

    return ApiResponse(
        message="Career report fetched successfully.",
        data=report,
    )