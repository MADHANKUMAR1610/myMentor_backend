"""Course business logic."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.course import Course as CourseModel
from app.models.enrollment import Enrollment
from app.repositories.course_repository import CourseRepository
from app.repositories.level_repository import LevelRepository
from app.schemas import Course, CourseCreate, gen_id

logger = logging.getLogger(__name__)


class CourseService:
    """Handle course and enrollment business logic."""

    def __init__(self, db: AsyncSession):
        self.course_repository = CourseRepository(db)
        self.level_repository = LevelRepository(db)

    async def list_courses(
        self,
        user_id: str,
    ) -> list[dict]:

        courses = await self.course_repository.get_all()

        enrollments = await self.course_repository.get_user_enrollments(
            user_id
        )

        enrolled_ids = {
            enrollment.course_id
            for enrollment in enrollments
        }

        return [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "thumbnail_url": course.thumbnail_url,
                "language": course.language,
                "difficulty": course.difficulty,
                "duration_hours": course.duration_hours,
                "status": course.status,
                "enrolled": course.id in enrolled_ids,
            }
            for course in courses
        ]

    async def get_course(
        self,
        course_id: str,
        user_id: str,
    ) -> dict:

        course = await self.course_repository.get_by_id(
            course_id
        )

        if course is None:
            raise NotFoundException("Course not found")

        enrollment = await self.course_repository.get_enrollment(
            user_id,
            course_id,
        )

        # Get all levels for this course
        levels = await self.level_repository.get_by_course(
            course_id
        )

        return {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "thumbnail_url": course.thumbnail_url,
            "language": course.language,
            "difficulty": course.difficulty,
            "duration_hours": course.duration_hours,
            "status": course.status,
            "enrolled": enrollment is not None,

            "levels": [
                {
                    "id": level.id,
                    "title": level.title,
                    "stage": level.stage,
                    "level_number": level.level_number,
                    "description": level.description,
                    "xp_reward": level.xp_reward,
                    "pass_percentage": level.pass_percentage,
                    "estimated_minutes": level.estimated_minutes,
                    "video_url": level.video_url,
                    "video_duration_seconds": level.video_duration_seconds,
                    "theory_html": level.theory_html,
                    "notes_url": level.notes_url,
                }
                for level in levels
            ],
        }

    async def create_course(
        self,
        payload: CourseCreate,
    ) -> Course:

        course = CourseModel(
            id=gen_id(),
            **payload.model_dump(),
        )

        await self.course_repository.create(course)

        return Course.model_validate(course)

    async def enroll(
        self,
        course_id: str,
        user_id: str,
    ) -> dict:

        course = await self.course_repository.get_by_id(
            course_id
        )

        if course is None:
            raise NotFoundException("Course not found")

        existing = await self.course_repository.get_enrollment(
            user_id,
            course_id,
        )

        if existing:
            raise BadRequestException(
                "Already enrolled"
            )

        enrollment = Enrollment(
            id=gen_id(),
            user_id=user_id,
            course_id=course_id,
        )

        await self.course_repository.create_enrollment(
            enrollment
        )

        return {
            "course_id": course_id,
            "enrolled": True,
        }