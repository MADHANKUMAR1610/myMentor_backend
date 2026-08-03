"""Progress and submission database operations."""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import Progress
from app.models.submission import Submission

logger = logging.getLogger(__name__)

MAX_RESULTS = 1000


class ProgressRepository:
    """Repository for progress and submission operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_and_level(
        self,
        user_id: str,
        level_id: str,
    ) -> Optional[Progress]:
        """Return progress for a user and level."""

        logger.debug(
            "Fetching progress for user=%s level=%s",
            user_id,
            level_id,
        )

        result = await self.db.execute(
            select(Progress).where(
                Progress.user_id == user_id,
                Progress.level_id == level_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_and_course(
        self,
        user_id: str,
        course_id: str,
    ) -> list[Progress]:
        """Return all progress records for a course."""

        logger.debug(
            "Fetching course progress. User=%s Course=%s",
            user_id,
            course_id,
        )

        result = await self.db.execute(
            select(Progress).where(
                Progress.user_id == user_id,
                Progress.course_id == course_id,
            )
        )

        return result.scalars().all()

    async def get_by_user(
        self,
        user_id: str,
    ) -> list[Progress]:
        """Return all progress records for a user."""

        logger.debug(
            "Fetching all progress for user=%s",
            user_id,
        )

        result = await self.db.execute(
            select(Progress).where(
                Progress.user_id == user_id,
            )
        )

        return result.scalars().all()

    async def save(
        self,
        progress: Progress,
    ) -> None:
        """Insert or update progress."""

        logger.debug(
            "Saving progress. User=%s Level=%s",
            progress.user_id,
            progress.level_id,
        )

        existing = await self.get_by_user_and_level(
            progress.user_id,
            progress.level_id,
        )

        if existing:
            existing.video_watched_seconds = progress.video_watched_seconds
            existing.video_completed = progress.video_completed
            existing.completed = progress.completed
            existing.xp_earned = progress.xp_earned
            existing.updated_at = datetime.utcnow()
        else:
            self.db.add(progress)

        await self.db.commit()

    async def create_submission(
        self,
        submission: Submission,
    ) -> None:
        """Insert a new code submission."""

        logger.debug(
            "Creating submission %s",
            submission.id,
        )

        self.db.add(submission)
        await self.db.commit()

    async def count_completed_levels(
        self,
        user_id: str | None = None,
        course_id: str | None = None,
    ) -> int:
        """Return completed level count."""

        stmt = select(func.count()).select_from(Progress).where(
            Progress.completed.is_(True)
        )

        if user_id:
            stmt = stmt.where(Progress.user_id == user_id)

        if course_id:
            stmt = stmt.where(Progress.course_id == course_id)

        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def count_completed_by_user_and_course(
        self,
        user_id: str,
        course_id: str,
    ) -> int:
        """Return completed levels for a user in a course."""

        result = await self.db.execute(
            select(func.count()).select_from(Progress).where(
                Progress.user_id == user_id,
                Progress.course_id == course_id,
                Progress.completed.is_(True),
            )
        )

        return result.scalar_one()

    async def count_submissions(self) -> int:
        """Return total submission count."""

        result = await self.db.execute(
            select(func.count()).select_from(Submission)
        )

        return result.scalar_one()

    async def get_active_user_ids_since(
        self,
        timestamp: datetime,
    ) -> list[str]:
        """Return active users since a timestamp."""

        result = await self.db.execute(
            select(Progress.user_id)
            .where(Progress.updated_at >= timestamp)
            .distinct()
        )

        return result.scalars().all()

    async def get_user_progress(
        self,
        user_id: str,
    ) -> list[Progress]:
        """Return user progress."""

        result = await self.db.execute(
            select(Progress).where(
                Progress.user_id == user_id,
            )
        )

        return result.scalars().all()

    async def get_continue_learning(
        self,
        user_id: str,
    ) -> Optional[Progress]:
        """Return the student's next level to continue."""

        result = await self.db.execute(
            select(Progress).where(
                Progress.user_id == user_id,
                Progress.completed.is_(False),
            )
        )

        return result.scalar_one_or_none()