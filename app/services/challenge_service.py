"""Challenge and checkpoint business logic."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge as ChallengeModel
from app.models.checkpoint import Checkpoint as CheckpointModel
from app.repositories.challenge_repository import ChallengeRepository
from app.schemas import (
    Challenge,
    ChallengeCreate,
    Checkpoint,
    CheckpointCreate,
)
from app.schemas.common import gen_id

logger = logging.getLogger(__name__)


class ChallengeService:
    """Handle challenge and checkpoint business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.challenge_repository = ChallengeRepository(db)

    async def create_challenge(
        self,
        payload: ChallengeCreate,
    ) -> Challenge:
        """Create a new coding challenge."""

        logger.info(
            "Creating challenge '%s'",
            payload.title,
        )

        challenge = ChallengeModel(
            id=gen_id(),
            **payload.model_dump(),
        )

        await self.challenge_repository.create_challenge(
            challenge,
        )

        logger.info(
            "Challenge created successfully. ID=%s",
            challenge.id,
        )

        return Challenge.model_validate(challenge)

    async def create_checkpoint(
        self,
        payload: CheckpointCreate,
    ) -> Checkpoint:
        """Create a new checkpoint."""

        logger.info(
            "Creating checkpoint for level '%s'",
            payload.level_id,
        )

        checkpoint = CheckpointModel(
            id=gen_id(),
            **payload.model_dump(),
        )

        await self.challenge_repository.create_checkpoint(
            checkpoint,
        )

        logger.info(
            "Checkpoint created successfully. ID=%s",
            checkpoint.id,
        )

        return Checkpoint.model_validate(checkpoint)