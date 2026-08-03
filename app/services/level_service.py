"""Level business logic."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level as LevelModel
from app.models.user import User
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.level_repository import LevelRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas import Level, LevelCreate
from app.schemas.common import gen_id

logger = logging.getLogger(__name__)


class LevelService:
    """Handle level business logic."""

    def __init__(self, db: AsyncSession):
        self.level_repository = LevelRepository(db)
        self.challenge_repository = ChallengeRepository(db)
        self.progress_repository = ProgressRepository(db)

    async def get_level(
        self,
        level_id: str,
        user: User,
    ) -> dict:
        """Return level details with checkpoints."""

        logger.info(
            "Fetching level %s for user %s",
            level_id,
            user.id,
        )

        level = await self.level_repository.get_by_id(level_id)

        if level is None:
            logger.warning(
                "Level %s not found",
                level_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Level not found",
            )

        checkpoints = await self.challenge_repository.get_checkpoints_by_level(
            level_id
        )

        checkpoints.sort(key=lambda checkpoint: checkpoint.order)

        challenge_ids = [
            checkpoint.challenge_id
            for checkpoint in checkpoints
        ]

        challenges = await self.challenge_repository.get_challenges_by_ids(
            challenge_ids
        )

        challenges_by_id = {
            challenge.id: challenge
            for challenge in challenges
        }

        checkpoint_data = []

        for checkpoint in checkpoints:

            challenge = challenges_by_id.get(
                checkpoint.challenge_id
            )

            challenge_data = None

            if challenge:
                challenge_data = {
                    "id": challenge.id,
                    "title": challenge.title,
                    "business_scenario": challenge.business_scenario,
                    "problem_statement": challenge.problem_statement,
                    "difficulty": challenge.difficulty,
                    "language": challenge.language,
                    "starter_code": challenge.starter_code,
                    "expected_output": challenge.expected_output,
                    "constraints": challenge.constraints,
                    "hints": challenge.hints,
                    "solution": challenge.solution,
                    "explanation": challenge.explanation,
                    "marks": challenge.marks,
                    "xp": challenge.xp,
                    "retry_limit": challenge.retry_limit,
                    "test_cases": challenge.test_cases,
                    "created_at": challenge.created_at,
                    "updated_at": challenge.updated_at,
                }

                if user.role != "admin":
                    challenge_data["solution"] = None

                    challenge_data["test_cases"] = [
                        self._sanitize_test_case(test_case)
                        for test_case in challenge_data.get(
                            "test_cases",
                            [],
                        )
                    ]

            checkpoint_data.append(
                {
                    "id": checkpoint.id,
                    "order": checkpoint.order,
                    "timestamp_seconds": checkpoint.timestamp_seconds,
                    "challenge": challenge_data,
                }
            )

        progress = await self.progress_repository.get_by_user_and_level(
            user.id,
            level_id,
        )

        logger.info(
            "Level %s returned successfully",
            level_id,
        )

        return {
            "level": Level.model_validate(level),
            "checkpoints": checkpoint_data,
            "progress": progress,
        }

    async def create_level(
        self,
        payload: LevelCreate,
    ) -> Level:
        """Create a new level."""

        logger.info(
            "Creating level %s",
            payload.title,
        )

        level = LevelModel(
            id=gen_id(),
            course_id=payload.course_id,
            stage=payload.stage,
            level_number=payload.level_number,
            title=payload.title,
            description=payload.description,
            xp_reward=payload.xp_reward,
            pass_percentage=payload.pass_percentage,
            estimated_minutes=payload.estimated_minutes,
            video_url=payload.video_url,
            video_duration_seconds=payload.video_duration_seconds,
            theory_html=payload.theory_html,
            notes_url=payload.notes_url,
        )

        await self.level_repository.create(level)

        logger.info(
            "Level created successfully. ID=%s",
            level.id,
        )

        return Level.model_validate(level)

    @staticmethod
    def _sanitize_test_case(
        test_case: dict,
    ) -> dict:
        """Hide expected output for hidden test cases."""

        if not test_case.get("is_hidden"):
            return test_case

        return {
            key: value
            for key, value in test_case.items()
            if key != "expected_output"
        }