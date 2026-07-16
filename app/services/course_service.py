"""Course business logic."""

import logging

from app.core.exceptions import NotFoundException
from app.repositories import (
    course_repository,
    level_repository,
    progress_repository,
)
from app.schemas import (
    Course,
    CourseCreate,
    Enrollment,
)

logger = logging.getLogger(__name__)

STAGE_ORDER = {
    "Beginner": 0,
    "Intermediate": 1,
    "Expert": 2,
}


class CourseService:
    """Handle course and enrollment business logic."""

    def __init__(self) -> None:
        self.course_repository = course_repository
        self.level_repository = level_repository
        self.progress_repository = progress_repository

    async def list_courses(
        self,
        user_id: str,
    ) -> list[dict]:
        """Return all courses with enrollment status."""

        logger.info(
            "Fetching courses for user %s",
            user_id,
        )

        courses = await self.course_repository.get_all()

        enrollments = (
            await self.course_repository.get_user_enrollments(
                user_id,
            )
        )

        enrolled_course_ids = {
            enrollment["course_id"]
            for enrollment in enrollments
        }

        for course in courses:
            course["is_enrolled"] = (
                course["id"] in enrolled_course_ids
            )

        logger.info(
            "Returned %s courses",
            len(courses),
        )

        return courses

    async def get_course(
        self,
        course_id: str,
        user_id: str,
    ) -> dict:
        """Return course details with level progress."""

        logger.info(
            "Fetching course %s for user %s",
            course_id,
            user_id,
        )

        course = await self.course_repository.get_by_id(
            course_id,
        )

        if not course:
            logger.warning(
                "Course not found: %s",
                course_id,
            )

            raise NotFoundException(
                "Course not found",
            )

        levels = await self.level_repository.get_by_course(
            course_id,
        )

        levels.sort(
            key=lambda level: (
                STAGE_ORDER.get(
                    level["stage"],
                    999,
                ),
                level["level_number"],
            )
        )

        progress_documents = (
            await self.progress_repository.get_by_user_and_course(
                user_id,
                course_id,
            )
        )

        progress_by_level = {
            progress["level_id"]: progress
            for progress in progress_documents
        }

        self._attach_progress(
            levels,
            progress_by_level,
        )

        course["levels"] = levels

        logger.info(
            "Course %s returned with %s levels",
            course_id,
            len(levels),
        )

        return course

    async def create_course(
        self,
        payload: CourseCreate,
    ) -> Course:
        """Create a new course."""

        logger.info(
            "Creating course '%s'",
            payload.title,
        )

        course = Course(
            **payload.model_dump()
        )

        await self.course_repository.create(
            course.model_dump()
        )

        logger.info(
            "Course created successfully. ID=%s",
            course.id,
        )

        return course

    async def enroll(
        self,
        course_id: str,
        user_id: str,
    ) -> dict:
        """Enroll a student in a course."""

        logger.info(
            "User %s enrolling in course %s",
            user_id,
            course_id,
        )

        existing = (
            await self.course_repository.get_enrollment(
                user_id,
                course_id,
            )
        )

        if existing:
            logger.info(
                "User %s already enrolled in course %s",
                user_id,
                course_id,
            )

            return {
                "enrolled": True,
            }

        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
        )

        await self.course_repository.create_enrollment(
            enrollment.model_dump()
        )

        logger.info(
            "Enrollment successful. User=%s Course=%s",
            user_id,
            course_id,
        )

        return {
            "enrolled": True,
        }

    def _attach_progress(
        self,
        levels: list[dict],
        progress_by_level: dict,
    ) -> None:
        """Attach progress information to each level."""

        previous_completed = True

        for level in levels:
            progress = progress_by_level.get(
                level["id"],
            )

            level["progress"] = progress or {
                "completed": False,
                "video_watched_seconds": 0,
                "checkpoints": [],
            }

            level["is_unlocked"] = previous_completed

            level["is_completed"] = bool(
                progress
                and progress.get(
                    "completed",
                )
            )

            previous_completed = level[
                "is_completed"
            ]


course_service = CourseService()