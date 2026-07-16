"""Challenge and checkpoint database operations."""

import logging
from typing import Optional

from app.database import get_database

logger = logging.getLogger(__name__)

MAX_RESULTS = 500

DEFAULT_PROJECTION = {
    "_id": 0,
}


class ChallengeRepository:
    """Repository for challenge and checkpoint operations."""

    @property
    def challenge_collection(self):
        """Return challenges collection."""
        return get_database().challenges

    @property
    def checkpoint_collection(self):
        """Return checkpoints collection."""
        return get_database().checkpoints

    async def get_challenge_by_id(
        self,
        challenge_id: str,
    ) -> Optional[dict]:
        """Return a challenge by its ID."""

        logger.debug(
            "Fetching challenge %s",
            challenge_id,
        )

        return await self.challenge_collection.find_one(
            {
                "id": challenge_id,
            },
            DEFAULT_PROJECTION,
        )

    async def get_challenges_by_ids(
        self,
        challenge_ids: list[str],
    ) -> list[dict]:
        """Return multiple challenges by IDs."""

        logger.debug(
            "Fetching %s challenges",
            len(challenge_ids),
        )

        return await self.challenge_collection.find(
            {
                "id": {
                    "$in": challenge_ids,
                }
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def create_challenge(
        self,
        challenge: dict,
    ) -> None:
        """Insert a new challenge."""

        logger.debug(
            "Creating challenge %s",
            challenge["id"],
        )

        await self.challenge_collection.insert_one(
            challenge,
        )

    async def get_checkpoint_by_id(
        self,
        checkpoint_id: str,
    ) -> Optional[dict]:
        """Return a checkpoint by its ID."""

        logger.debug(
            "Fetching checkpoint %s",
            checkpoint_id,
        )

        return await self.checkpoint_collection.find_one(
            {
                "id": checkpoint_id,
            },
            DEFAULT_PROJECTION,
        )

    async def get_checkpoints_by_level(
        self,
        level_id: str,
    ) -> list[dict]:
        """Return all checkpoints for a level."""

        logger.debug(
            "Fetching checkpoints for level %s",
            level_id,
        )

        return await self.checkpoint_collection.find(
            {
                "level_id": level_id,
            },
            DEFAULT_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def create_checkpoint(
        self,
        checkpoint: dict,
    ) -> None:
        """Insert a new checkpoint."""

        logger.debug(
            "Creating checkpoint %s",
            checkpoint["id"],
        )

        await self.checkpoint_collection.insert_one(
            checkpoint,
        )

    async def count_challenges(
        self,
    ) -> int:
        """Return total challenge count."""

        logger.debug(
            "Counting challenges",
        )

        return await self.challenge_collection.count_documents(
            {}
        )


challenge_repository = ChallengeRepository()