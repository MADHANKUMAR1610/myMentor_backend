"""Course API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    get_current_admin,
    get_current_user,
)
from app.database.postgres import get_db
from app.schemas import (
    ApiResponse,
    Course,
    CourseCreate,
)
from app.services.course_service import CourseService


router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


@router.get(
    "",
    response_model=ApiResponse[list[dict]],
    status_code=status.HTTP_200_OK,
    summary="List courses",
    description=(
        "Return all available courses along with "
        "the enrollment status for the authenticated user."
    ),
)
async def list_courses(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[dict]]:
    """Return available courses."""

    service = CourseService(db)

    courses = await service.list_courses(
        current_user.id,
    )

    return ApiResponse(
        message="Courses retrieved successfully",
        data=courses,
    )


@router.get(
    "/{course_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get course",
    description=(
        "Return detailed information about a course, "
        "including levels and user progress."
    ),
)
async def get_course(
    course_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Return course details."""

    service = CourseService(db)

    course = await service.get_course(
        course_id,
        current_user.id,
    )

    return ApiResponse(
        message="Course retrieved successfully",
        data=course,
    )


@router.post(
    "",
    response_model=ApiResponse[Course],
    status_code=status.HTTP_201_CREATED,
    summary="Create course",
    description="Create a new course. Admin access required.",
)
async def create_course(
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
) -> ApiResponse[Course]:
    """Create a course."""

    service = CourseService(db)

    course = await service.create_course(
        payload,
    )

    return ApiResponse(
        message="Course created successfully",
        data=course,
    )


@router.post(
    "/{course_id}/enroll",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Enroll in course",
    description=(
        "Enroll the authenticated user in the specified course."
    ),
)
async def enroll_course(
    course_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Enroll the authenticated user."""

    service = CourseService(db)

    result = await service.enroll(
        course_id,
        current_user.id,
    )

    return ApiResponse(
        message="Course enrolled successfully",
        data=result,
    )