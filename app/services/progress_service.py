"""Student progress business logic using PostgreSQL."""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.schemas.common import gen_id
from app.models.progress import Progress
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.level_repository import LevelRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.user_repository import UserRepository

from app.schemas import (
    CompleteCheckpointRequest,
    CompleteLevelRequest,
    VideoProgressRequest,
)

logger = logging.getLogger(__name__)

STAGE_ORDER = {
    "Beginner": 0,
    "Intermediate": 1,
    "Expert": 2,
}


class ProgressService:
    """Handle student learning progress."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.progress_repository = ProgressRepository(db)
        self.level_repository = LevelRepository(db)
        self.challenge_repository = ChallengeRepository(db)
        self.course_repository = CourseRepository(db)
        self.user_repository = UserRepository()

    async def complete_checkpoint(
        self,
        body: CompleteCheckpointRequest,
        user: dict,
    ) -> dict:
        """Mark a checkpoint as completed."""

        level_id = body.level_id
        checkpoint_id = body.checkpoint_id

        level = await self._get_level(level_id)

        logger.info(
            "User %s completing checkpoint %s",
            user.id,
            checkpoint_id,
        )

        progress = await self._get_or_create_progress(
            user.id,
            level.id,
            level.course_id,
        )

        checkpoints = progress.checkpoints or []

        existing_checkpoint = next(
            (
                checkpoint
                for checkpoint in checkpoints
                if checkpoint["checkpoint_id"] == checkpoint_id
            ),
            None,
        )

        xp_awarded = 0

        if existing_checkpoint:

            if not existing_checkpoint.get("completed", False):
                existing_checkpoint["completed"] = True
                existing_checkpoint["completed_at"] = (
                    datetime.utcnow().isoformat()
                )

                existing_checkpoint["submissions"] = (
                    existing_checkpoint.get(
                        "submissions",
                        0,
                    )
                    + 1
                )

        else:

            checkpoints.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "completed": True,
                    "completed_at": datetime.utcnow().isoformat(),
                    "submissions": 1,
                }
            )

        progress.checkpoints = checkpoints

        await self._save_progress(progress)

        if xp_awarded > 0:
            await self.user_repository.increment_xp(
                self.db,
                user.id,
                xp_awarded,
            )

        logger.info(
            "Checkpoint %s completed by user %s",
            checkpoint_id,
            user.id,
        )

        return {
        "ok": True,
        "progress": {
        "id": progress.id,
        "user_id": progress.user_id,
        "level_id": progress.level_id,
        "course_id": progress.course_id,
        "video_watched_seconds": progress.video_watched_seconds,
        "video_completed": progress.video_completed,
        "completed": progress.completed,
        "xp_earned": progress.xp_earned,
        "checkpoints": progress.checkpoints,
        "updated_at": (
            progress.updated_at.isoformat()
            if progress.updated_at
            else None
        ),
    },
}
    async def update_video_progress(
        self,
        body: VideoProgressRequest,
        user: dict,
    ) -> dict:
        """Update video watch progress."""

        level_id = body.level_id
        watched_seconds = body.watched_seconds

        level = await self._get_level(level_id)

        logger.info(
            "Updating video progress. "
            "User=%s Level=%s Seconds=%s",
          user.id,
            level_id,
            watched_seconds,
        )

        progress = await self._get_or_create_progress(
           user.id ,
            level.id,
            level.course_id,
        )

        progress.video_watched_seconds = max(
            progress.video_watched_seconds or 0,
            watched_seconds,
        )

        if (
            progress.video_watched_seconds
            >= (level.video_duration_seconds or 0) - 5
        ):
            progress.video_completed = True

        await self._save_progress(progress)

        logger.info(
            "Video progress updated. "
            "User=%s Level=%s",
           user.id ,
            level_id,
        )

        return {
            "ok": True,
        }

    async def _get_or_create_progress(
        self,
        user_id: str,
        level_id: str,
        course_id: str,
    ) -> Progress:
        """Return existing progress or create a new one."""

        progress = (
            await self.progress_repository.get_by_user_and_level(
                user_id,
                level_id,
            )
        )

        if progress:
            return progress

        logger.info(
            "Creating progress. User=%s Level=%s",
            user_id,
            level_id,
        )

        progress = Progress(
            id=gen_id(),
            user_id=user_id,
            level_id=level_id,
            course_id=course_id,
            completed=False,
            xp_earned=0,
            video_completed=False,
            video_watched_seconds=0,
            checkpoints=[],
        )

        await self.progress_repository.save(progress)

        return progress

    async def _save_progress(
        self,
        progress: Progress,
    ) -> None:
        """Persist student progress."""

        progress.updated_at = datetime.utcnow()

        await self.progress_repository.save(
            progress,
        )

        logger.debug(
            "Progress saved. User=%s Level=%s",
            progress.user_id,
            progress.level_id,
        )

    async def _get_level(
        self,
        level_id: str,
    ):
        """Return a level or raise a not-found exception."""

        level = await self.level_repository.get_by_id(
            level_id,
        )

        if not level:
            logger.warning(
                "Level not found: %s",
                level_id,
            )

            raise NotFoundException(
                "Level not found",
            )

        return level

    async def _get_checkpoints(
        self,
        level_id: str,
    ):
        """Return checkpoints for a level."""

        return await self.challenge_repository.get_checkpoints_by_level(
            level_id,
        )
    async def complete_level(
        self,
        body: CompleteLevelRequest,
        user: dict,
    ) -> dict:
        """Complete a level after validation."""

        level_id = body.level_id

        logger.info(
            "User %s attempting to complete level %s",
           user.id ,
            level_id,
        )

        level = await self._get_level(level_id)

        progress = await self._validate_level_completion(
            level,
            user,
        )

        if progress.completed:
            logger.info(
                "Level %s already completed by user %s",
                level_id,
                user.id,
            )

            return {
                "ok": True,
                "xp_earned": 0,
            }

        xp_reward = int(level.xp_reward or 100)

        progress.completed = True
        progress.completed_at = datetime.utcnow()
        progress.xp_earned = (
            progress.xp_earned or 0
        ) + xp_reward

        await self._save_progress(progress)

        await self._award_xp(
            user.id,
            xp_reward,
        )

        logger.info(
            "Level %s completed successfully by user %s. XP=%s",
            level_id,
            user.id,
            xp_reward,
        )

        return {
            "ok": True,
            "xp_earned": xp_reward,
        }

    async def _validate_level_completion(
        self,
        level,
        user: dict,
    ) -> Progress:
        """Validate whether a level can be completed."""

        progress = (
            await self.progress_repository.get_by_user_and_level(
                user.id,
                level.id,
            )
        )

        if not progress:
            logger.warning(
                "No progress found. User=%s Level=%s",
                user.id,
                level.id,
            )

            raise BadRequestException(
                "No progress yet"
            )

        checkpoints = await self._get_checkpoints(
            level.id,
        )

        required_checkpoint_ids = {
            checkpoint.id
            for checkpoint in checkpoints
        }

        completed_checkpoint_ids = {
            checkpoint["checkpoint_id"]
            for checkpoint in (progress.checkpoints or [])
            if checkpoint.get("completed", False)
        }

        missing_checkpoint_ids = (
            required_checkpoint_ids
            - completed_checkpoint_ids
        )

        if missing_checkpoint_ids:
            logger.warning(
                "Checkpoint validation failed. "
                "User=%s Level=%s Missing=%s",
                user.id,
                level.id,
                len(missing_checkpoint_ids),
            )

            raise BadRequestException(
                "Complete all checkpoints first"
            )

        self._validate_video_completion(
            progress,
            level,
        )

        return progress

    def _validate_video_completion(
        self,
        progress: Progress,
        level,
    ) -> None:
        """Ensure the required video has been watched."""

        if progress.video_completed:
            return

        watched_seconds = int(
            progress.video_watched_seconds or 0
        )

        video_duration = int(
            level.video_duration_seconds or 0
        )

        required_seconds = (
            video_duration * 0.85
        )

        if watched_seconds < required_seconds:
            logger.warning(
                "Video completion validation failed. "
                "Level=%s Watched=%s Required=%s",
                level.id,
                watched_seconds,
                required_seconds,
            )

            raise BadRequestException(
                "Watch the full video first"
            )
    async def _award_xp(
        self,
        user_id: str,
        xp: int,
    ) -> None:
        """Award XP and update streak."""

        if xp <= 0:
            return

        await self.user_repository.increment_xp_and_streak(
            self.db,
            user_id,
            xp,
        )

        logger.info(
            "Awarded %s XP to user %s",
            xp,
            user_id,
        )

    async def get_dashboard(
        self,
        user: dict,
    ) -> dict:
        """Return dashboard information for the logged-in user."""

        profile = await self.user_repository.get_public_by_id(
            self.db,
            user.id,
        )

        if not profile:
            raise NotFoundException(
                "User not found"
            )

        enrollments = (
            await self.course_repository.get_user_enrollments(
                user.id,
            )
        )

        completed_levels = (
            await self.progress_repository.count_completed_levels(
                user.id,
            )
        )

        continue_learning = (
            await self.progress_repository.get_continue_learning(
                user.id,
            )
        )

        course_cards = (
            await self.course_repository.get_dashboard_courses(
                user.id,
            )
        )

        leaderboard = (
            await self.user_repository.get_leaderboard_summary(
                self.db,
                user.id,
            )
        )

        return {
            "user": {
                "id": profile.id,
                "name": profile.name,
                "email": profile.email,
                "avatar_url": profile.avatar_url,
                "xp": profile.xp,
                "streak": profile.streak_count,
            },
            "stats": {
                "current_xp": profile.xp,
                "streak": profile.streak_count,
                "courses": len(enrollments),
                "levels_cleared": completed_levels,
            },
            "continue_learning": (
    {
        "id": continue_learning.id,
        "level_id": continue_learning.level_id,
        "course_id": continue_learning.course_id,
        "completed": continue_learning.completed,
        "video_completed": continue_learning.video_completed,
        "video_watched_seconds": continue_learning.video_watched_seconds,
        "xp_earned": continue_learning.xp_earned,
    }
    if continue_learning
    else None
),
            "courses": course_cards,
            "leaderboard": leaderboard,
        }