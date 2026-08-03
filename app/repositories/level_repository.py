"""Level database operations."""

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level

logger = logging.getLogger(__name__)

MAX_RESULTS = 1000


class LevelRepository:
    """Repository for level operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        level_id: str,
    ) -> Optional[Level]:
        """Return a level by its ID."""

        logger.debug("Fetching level %s", level_id)

        result = await self.db.execute(
            select(Level).where(Level.id == level_id)
        )

        return result.scalar_one_or_none()

    async def get_by_ids(
        self,
        level_ids: list[str],
    ) -> list[Level]:
        """Return multiple levels by IDs."""

        logger.debug("Fetching %s levels", len(level_ids))

        result = await self.db.execute(
            select(Level).where(Level.id.in_(level_ids))
        )

        return result.scalars().all()

    async def get_by_course(
        self,
        course_id: str,
    ) -> list[Level]:
        """Return all levels for a course."""

        logger.debug("Fetching levels for course %s", course_id)

        result = await self.db.execute(
            select(Level)
            .where(Level.course_id == course_id)
            .order_by(Level.stage, Level.level_number)
        )

        return result.scalars().all()

    async def create(
        self,
        level: Level,
    ) -> None:
        """Insert a new level."""

        logger.debug("Creating level %s", level.id)

        self.db.add(level)
        await self.db.commit()
        await self.db.refresh(level)

    async def count_by_course(
        self,
        course_id: str,
    ) -> int:
        """Return total levels for a course."""

        logger.debug("Counting levels for course %s", course_id)

        result = await self.db.execute(
            select(func.count())
            .select_from(Level)
            .where(Level.course_id == course_id)
        )

        return result.scalar_one()

    async def count_levels(
        self,
    ) -> int:
        """Return total level count."""

        logger.debug("Counting levels")

        result = await self.db.execute(
            select(func.count()).select_from(Level)
        )

        return result.scalar_one()