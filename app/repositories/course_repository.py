"""Course and enrollment database operations."""

import logging
from typing import Optional

from app.database import get_database

logger = logging.getLogger(__name__)

MAX_RESULTS = 500

DEFAULT_PROJECTION = {
    "_id": 0,
}


class CourseRepository:
    """Repository for course and enrollment operations."""

    @property
    def course_collection(self):
        """Return courses collection."""
        return get_database().courses

    @property
    def enrollment_collection(self):
        """Return enrollments collection."""
        return get_database().enrollments

    async def get_all(
        self,
    ) -> list[dict]:
        """Return all courses."""

        logger.debug("Fetching all courses")

        return await self.course_collection.find(
            {},
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def get_by_id(
        self,
        course_id: str,
    ) -> Optional[dict]:
        """Return a course by ID."""

        logger.debug(
            "Fetching course %s",
            course_id,
        )

        return await self.course_collection.find_one(
            {
                "id": course_id,
            },
            DEFAULT_PROJECTION,
        )

    async def get_by_ids(
        self,
        course_ids: list[str],
    ) -> list[dict]:
        """Return multiple courses by IDs."""

        logger.debug(
            "Fetching %s courses",
            len(course_ids),
        )

        return await self.course_collection.find(
            {
                "id": {
                    "$in": course_ids,
                }
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def create(
        self,
        course: dict,
    ) -> None:
        """Insert a new course."""

        logger.debug(
            "Creating course %s",
            course["id"],
        )

        await self.course_collection.insert_one(
            course,
        )

    async def get_user_enrollments(
        self,
        user_id: str,
    ) -> list[dict]:
        """Return all enrollments for a user."""

        logger.debug(
            "Fetching enrollments for user %s",
            user_id,
        )

        return await self.enrollment_collection.find(
            {
                "user_id": user_id,
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def get_enrollment(
        self,
        user_id: str,
        course_id: str,
    ) -> Optional[dict]:
        """Return a user's enrollment."""

        logger.debug(
            "Checking enrollment. User=%s Course=%s",
            user_id,
            course_id,
        )

        return await self.enrollment_collection.find_one(
            {
                "user_id": user_id,
                "course_id": course_id,
            },
            DEFAULT_PROJECTION,
        )

    async def create_enrollment(
        self,
        enrollment: dict,
    ) -> None:
        """Insert a new enrollment."""

        logger.debug(
            "Creating enrollment %s",
            enrollment["id"],
        )

        await self.enrollment_collection.insert_one(
            enrollment,
        )

    async def count_courses(
        self,
    ) -> int:
        """Return total course count."""

        logger.debug(
            "Counting courses",
        )

        return await self.course_collection.count_documents(
            {}
        )


course_repository = CourseRepository()