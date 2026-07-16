"""Level business logic."""

import logging

from fastapi import HTTPException, status

from app.repositories import (
    challenge_repository,
    level_repository,
    progress_repository,
)
from app.schemas import (
    Level,
    LevelCreate,
)

logger = logging.getLogger(__name__)


class LevelService:
    """Handle level business logic."""

    def __init__(self) -> None:
        self.level_repository = level_repository
        self.challenge_repository = challenge_repository
        self.progress_repository = progress_repository

    async def get_level(
        self,
        level_id: str,
        user: dict,
    ) -> dict:
        """Return level details with checkpoints."""

        logger.info(
            "Fetching level %s for user %s",
            level_id,
            user["id"],
        )

        level = await self.level_repository.get_by_id(
            level_id
        )

        if not level:
            logger.warning(
                "Level not found: %s",
                level_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Level not found",
            )

        checkpoints = (
            await self.challenge_repository.get_checkpoints_by_level(
                level_id
            )
        )

        checkpoints.sort(
            key=lambda checkpoint: checkpoint["order"]
        )

        challenge_ids = [
            checkpoint["challenge_id"]
            for checkpoint in checkpoints
        ]

        challenges = (
            await self.challenge_repository.get_challenges_by_ids(
                challenge_ids
            )
        )

        challenges_by_id = {
            challenge["id"]: challenge
            for challenge in challenges
        }

        self._attach_challenges(
            checkpoints,
            challenges_by_id,
            user["role"],
        )

        level["checkpoints"] = checkpoints

        progress = (
            await self.progress_repository.get_by_user_and_level(
                user["id"],
                level_id,
            )
        )

        level["progress"] = progress

        logger.info(
            "Level %s returned with %s checkpoints",
            level_id,
            len(checkpoints),
        )

        return level

    async def create_level(
        self,
        payload: LevelCreate,
    ) -> Level:
        """Create a new level."""

        logger.info(
            "Creating level %s",
            payload.title,
        )

        level = Level(
            **payload.model_dump()
        )

        await self.level_repository.create(
            level.model_dump()
        )

        logger.info(
            "Level created successfully. Level ID: %s",
            level.id,
        )

        return level

    def _attach_challenges(
        self,
        checkpoints: list[dict],
        challenges_by_id: dict[str, dict],
        role: str,
    ) -> None:
        """Attach challenge information to checkpoints."""

        for checkpoint in checkpoints:
            challenge = (
                challenges_by_id.get(
                    checkpoint["challenge_id"],
                    {},
                ).copy()
            )

            if role != "admin":
                challenge.pop(
                    "solution",
                    None,
                )

                challenge["test_cases"] = [
                    self._sanitize_test_case(
                        test_case
                    )
                    for test_case in challenge.get(
                        "test_cases",
                        [],
                    )
                ]

            checkpoint["challenge"] = challenge

    @staticmethod
    def _sanitize_test_case(
        test_case: dict,
    ) -> dict:
        """Hide expected output for hidden test cases."""

        if not test_case.get(
            "is_hidden",
        ):
            return test_case

        return {
            key: value
            for key, value in test_case.items()
            if key != "expected_output"
        }


level_service = LevelService()