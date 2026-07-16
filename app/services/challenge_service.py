"""Challenge and checkpoint business logic."""

import logging

from app.repositories import challenge_repository
from app.schemas import (
    Challenge,
    ChallengeCreate,
    Checkpoint,
    CheckpointCreate,
)

logger = logging.getLogger(__name__)


class ChallengeService:
    """Handle challenge and checkpoint business logic."""

    def __init__(self) -> None:
        self.challenge_repository = challenge_repository

    async def create_challenge(
        self,
        payload: ChallengeCreate,
    ) -> Challenge:
        """Create a new coding challenge."""

        logger.info(
            "Creating challenge '%s'",
            payload.title,
        )

        challenge = Challenge(
            **payload.model_dump()
        )

        await self.challenge_repository.create_challenge(
            challenge.model_dump()
        )

        logger.info(
            "Challenge created successfully. ID=%s",
            challenge.id,
        )

        return challenge

    async def create_checkpoint(
        self,
        payload: CheckpointCreate,
    ) -> Checkpoint:
        """Create a new checkpoint."""

        logger.info(
            "Creating checkpoint for level '%s'",
            payload.level_id,
        )

        checkpoint = Checkpoint(
            **payload.model_dump()
        )

        await self.challenge_repository.create_checkpoint(
            checkpoint.model_dump()
        )

        logger.info(
            "Checkpoint created successfully. ID=%s",
            checkpoint.id,
        )

        return checkpoint


challenge_service = ChallengeService()