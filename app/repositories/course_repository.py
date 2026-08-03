"""Course and enrollment database operations."""

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.enrollment import Enrollment

logger = logging.getLogger(__name__)

MAX_RESULTS = 500


class CourseRepository:
    """Repository for course and enrollment operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Course]:
        logger.debug("Fetching all courses")

        result = await self.db.execute(
            select(Course).limit(MAX_RESULTS)
        )
        return result.scalars().all()

    async def get_by_id(
        self,
        course_id: str,
    ) -> Optional[Course]:

        logger.debug("Fetching course %s", course_id)

        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def get_by_ids(
        self,
        course_ids: list[str],
    ) -> list[Course]:

        logger.debug("Fetching %s courses", len(course_ids))

        result = await self.db.execute(
            select(Course).where(Course.id.in_(course_ids))
        )
        return result.scalars().all()

    async def create(
        self,
        course: Course,
    ) -> None:

        logger.debug("Creating course %s", course.id)

        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)

    async def get_user_enrollments(
        self,
        user_id: str,
    ) -> list[Enrollment]:

        logger.debug("Fetching enrollments for user %s", user_id)

        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id
            )
        )
        return result.scalars().all()

    async def get_enrollment(
        self,
        user_id: str,
        course_id: str,
    ) -> Optional[Enrollment]:

        logger.debug(
            "Checking enrollment. User=%s Course=%s",
            user_id,
            course_id,
        )

        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
            )
        )

        return result.scalar_one_or_none()

    async def create_enrollment(
        self,
        enrollment: Enrollment,
    ) -> None:

        logger.debug(
            "Creating enrollment %s",
            enrollment.id,
        )

        self.db.add(enrollment)
        await self.db.commit()
        await self.db.refresh(enrollment)

    async def count_courses(self) -> int:

        logger.debug("Counting courses")

        result = await self.db.execute(
            select(func.count()).select_from(Course)
        )

        return result.scalar_one()

    async def get_dashboard_courses(
        self,
        user_id: str,
    ) -> list[dict]:

        logger.debug(
            "Fetching dashboard courses for user=%s",
            user_id,
        )

        enrollments = await self.get_user_enrollments(user_id)

        if not enrollments:
            return []

        course_ids = [e.course_id for e in enrollments]

        courses = await self.get_by_ids(course_ids)

        dashboard = []

        for course in courses:
            dashboard.append(
                {
                    "course_id": course.id,
                    "title": course.title,
                    "thumbnail": course.thumbnail_url,
                    "description": course.description,
                    "progress_percentage": 0,
                    "completed_lessons": 0,
                    "total_lessons": 0,
                }
            )

        return dashboard