"""Level database operations."""

import logging
from typing import Optional

from app.database import get_database

logger = logging.getLogger(__name__)

MAX_RESULTS = 1000

DEFAULT_PROJECTION = {
    "_id": 0,
}


class LevelRepository:
    """Repository for level collection operations."""

    @property
    def collection(self):
        """Return levels collection."""
        return get_database().levels

    async def get_by_id(
        self,
        level_id: str,
    ) -> Optional[dict]:
        """Return a level by its ID."""

        logger.debug(
            "Fetching level %s",
            level_id,
        )

        return await self.collection.find_one(
            {"id": level_id},
            DEFAULT_PROJECTION,
        )

    async def get_by_ids(
        self,
        level_ids: list[str],
    ) -> list[dict]:
        """Return multiple levels by IDs."""

        logger.debug(
            "Fetching %s levels",
            len(level_ids),
        )

        return await self.collection.find(
            {
                "id": {
                    "$in": level_ids,
                }
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def get_by_course(
        self,
        course_id: str,
    ) -> list[dict]:
        """Return all levels for a course."""

        logger.debug(
            "Fetching levels for course %s",
            course_id,
        )

        return await self.collection.find(
            {
                "course_id": course_id,
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def create(
        self,
        level: dict,
    ) -> None:
        """Insert a new level."""

        logger.debug(
            "Creating level %s",
            level["id"],
        )

        await self.collection.insert_one(
            level,
        )

    async def count_by_course(
        self,
        course_id: str,
    ) -> int:
        """Return total levels for a course."""

        logger.debug(
            "Counting levels for course %s",
            course_id,
        )

        return await self.collection.count_documents(
            {
                "course_id": course_id,
            }
        )

    async def count_levels(self) -> int:
        """Return total level count."""

        logger.debug(
            "Counting levels",
        )

        return await self.collection.count_documents(
            {}
        )


level_repository = LevelRepository()