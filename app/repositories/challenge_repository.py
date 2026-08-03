"""Challenge and checkpoint database operations."""

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge
from app.models.checkpoint import Checkpoint

logger = logging.getLogger(__name__)

MAX_RESULTS = 500


class ChallengeRepository:
    """Repository for challenge and checkpoint operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_challenge_by_id(
        self,
        challenge_id: str,
    ) -> Optional[Challenge]:
        """Return a challenge by its ID."""

        logger.debug(
            "Fetching challenge %s",
            challenge_id,
        )

        result = await self.db.execute(
            select(Challenge).where(
                Challenge.id == challenge_id
            )
        )

        return result.scalar_one_or_none()

    async def get_challenges_by_ids(
        self,
        challenge_ids: list[str],
    ) -> list[Challenge]:
        """Return multiple challenges by IDs."""

        logger.debug(
            "Fetching %s challenges",
            len(challenge_ids),
        )

        result = await self.db.execute(
            select(Challenge).where(
                Challenge.id.in_(challenge_ids)
            )
        )

        return result.scalars().all()

    async def create_challenge(
        self,
        challenge: Challenge,
    ) -> None:
        """Insert a new challenge."""

        logger.debug(
            "Creating challenge %s",
            challenge.id,
        )

        self.db.add(challenge)
        await self.db.commit()
        await self.db.refresh(challenge)

    async def get_checkpoint_by_id(
        self,
        checkpoint_id: str,
    ) -> Optional[Checkpoint]:
        """Return a checkpoint by its ID."""

        logger.debug(
            "Fetching checkpoint %s",
            checkpoint_id,
        )

        result = await self.db.execute(
            select(Checkpoint).where(
                Checkpoint.id == checkpoint_id
            )
        )

        return result.scalar_one_or_none()

    async def get_checkpoints_by_level(
        self,
        level_id: str,
    ) -> list[Checkpoint]:
        """Return all checkpoints for a level."""

        logger.debug(
            "Fetching checkpoints for level %s",
            level_id,
        )

        result = await self.db.execute(
            select(Checkpoint).where(
                Checkpoint.level_id == level_id
            )
        )

        return result.scalars().all()

    async def create_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> None:
        """Insert a new checkpoint."""

        logger.debug(
            "Creating checkpoint %s",
            checkpoint.id,
        )

        self.db.add(checkpoint)
        await self.db.commit()
        await self.db.refresh(checkpoint)
    async def count_challenges(
        self,
    ) -> int:
        """Return total challenge count."""

        logger.debug(
            "Counting challenges",
        )

        result = await self.db.execute(
            select(func.count()).select_from(Challenge)
        )

        return result.scalar_one()