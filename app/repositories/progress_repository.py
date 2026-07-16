"""Progress and submission database operations."""

import logging
from typing import Optional

from app.database import get_database

logger = logging.getLogger(__name__)

MAX_RESULTS = 1000

DEFAULT_PROJECTION = {
    "_id": 0,
}


class ProgressRepository:
    """Repository for progress and submission operations."""

    @property
    def progress_collection(self):
        """Return progress collection."""
        return get_database().progress

    @property
    def submission_collection(self):
        """Return submissions collection."""
        return get_database().submissions

    async def get_by_user_and_level(
        self,
        user_id: str,
        level_id: str,
    ) -> Optional[dict]:
        """Return progress for a user and level."""

        logger.debug(
            "Fetching progress for user=%s level=%s",
            user_id,
            level_id,
        )

        return await self.progress_collection.find_one(
            {
                "user_id": user_id,
                "level_id": level_id,
            },
            DEFAULT_PROJECTION,
        )

    async def get_by_user_and_course(
        self,
        user_id: str,
        course_id: str,
    ) -> list[dict]:
        """Return all progress records for a course."""

        logger.debug(
            "Fetching course progress. User=%s Course=%s",
            user_id,
            course_id,
        )

        return await self.progress_collection.find(
            {
                "user_id": user_id,
                "course_id": course_id,
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def get_by_user(
        self,
        user_id: str,
    ) -> list[dict]:
        """Return all progress records for a user."""

        logger.debug(
            "Fetching all progress for user=%s",
            user_id,
        )

        return await self.progress_collection.find(
            {
                "user_id": user_id,
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def save(
        self,
        user_id: str,
        level_id: str,
        progress: dict,
    ) -> None:
        """Insert or update a progress document."""

        logger.debug(
            "Saving progress. User=%s Level=%s",
            user_id,
            level_id,
        )

        await self.progress_collection.update_one(
            {
                "user_id": user_id,
                "level_id": level_id,
            },
            {
                "$set": progress,
            },
            upsert=True,
        )

    async def create_submission(
        self,
        submission: dict,
    ) -> None:
        """Insert a new code submission."""

        logger.debug(
            "Creating submission %s",
            submission["id"],
        )

        await self.submission_collection.insert_one(
            submission,
        )

    async def count_completed_levels(
        self,
        user_id: str | None = None,
        course_id: str | None = None,
    ) -> int:
        """Return completed level count."""

        logger.debug(
            "Counting completed levels",
        )

        query = {
            "completed": True,
        }

        if user_id is not None:
            query["user_id"] = user_id

        if course_id is not None:
            query["course_id"] = course_id

        return await self.progress_collection.count_documents(
            query,
        )

    async def count_completed_by_user_and_course(
        self,
        user_id: str,
        course_id: str,
    ) -> int:
        """Return completed levels for a user in a course."""

        logger.debug(
            "Counting completed levels. User=%s Course=%s",
            user_id,
            course_id,
        )

        return await self.progress_collection.count_documents(
            {
                "user_id": user_id,
                "course_id": course_id,
                "completed": True,
            }
        )

    async def count_submissions(self) -> int:
        """Return total submission count."""

        logger.debug(
            "Counting submissions",
        )

        return await self.submission_collection.count_documents(
            {}
        )

    async def get_active_user_ids_since(
        self,
        timestamp: str,
    ) -> list[str]:
        """Return active users since a timestamp."""

        logger.debug(
            "Fetching active users since %s",
            timestamp,
        )

        return await self.progress_collection.distinct(
            "user_id",
            {
                "updated_at": {
                    "$gte": timestamp,
                }
            },
        )

    async def get_user_progress(
        self,
        user_id: str,
    ) -> list[dict]:
        """Return user progress."""

        logger.debug(
            "Fetching user progress for %s",
            user_id,
        )

        return await self.progress_collection.find(
            {
                "user_id": user_id,
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)


progress_repository = ProgressRepository()