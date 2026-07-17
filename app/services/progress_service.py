"""Student progress business logic."""

import logging

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.repositories import (
    challenge_repository,
    course_repository,
    level_repository,
    progress_repository,
    user_repository,
)
from app.schemas import (
    CompleteCheckpointRequest,
    CompleteLevelRequest,
    LevelProgress,
    VideoProgressRequest,
    utc_now_iso,
)

logger = logging.getLogger(__name__)

STAGE_ORDER = {
    "Beginner": 0,
    "Intermediate": 1,
    "Expert": 2,
}


class ProgressService:
    """Handle student learning progress."""

    def __init__(self) -> None:
        self.progress_repository = progress_repository
        self.level_repository = level_repository
        self.challenge_repository = challenge_repository
        self.course_repository = course_repository
        self.user_repository = user_repository

    async def complete_checkpoint(
        self,
        body: CompleteCheckpointRequest,
        user: dict,
    ) -> dict:
        """Mark a checkpoint as completed."""

        level_id = body.level_id
        checkpoint_id = body.checkpoint_id

        level = await self._get_level(
            level_id,
        )

        course_id = level["course_id"]

        logger.info(
            "User %s completing checkpoint %s",
            user["id"],
            checkpoint_id,
        )

        progress = await self._get_or_create_progress(
            user["id"],
            level_id,
            course_id,
        )

        checkpoints = progress.get(
            "checkpoints",
            [],
        )

        existing_checkpoint = next(
            (
                checkpoint
                for checkpoint in checkpoints
                if checkpoint["checkpoint_id"]
                == checkpoint_id
            ),
            None,
        )

        xp_awarded = 0

        if existing_checkpoint:

            if not existing_checkpoint.get(
                "completed",
                False,
            ):

                existing_checkpoint["completed"] = True
                existing_checkpoint["completed_at"] = (
                    utc_now_iso()
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
                    "submissions": 1,
                    "completed_at": utc_now_iso(),
                }
            )

        progress["checkpoints"] = checkpoints

        await self._save_progress(
            user["id"],
            level_id,
            progress,
        )

        if xp_awarded > 0:
            await self.user_repository.increment_xp(
                user["id"],
                xp_awarded,
            )

        logger.info(
            "Checkpoint %s completed by user %s",
            checkpoint_id,
            user["id"],
        )

        return {
            "ok": True,
            "progress": progress,
        }
    async def update_video_progress(
        self,
        body: VideoProgressRequest,
        user: dict,
    ) -> dict:
        """Update video watch progress."""

        level_id = body.level_id
        watched_seconds = body.watched_seconds

        level = await self._get_level(
            level_id,
        )

        course_id = level["course_id"]

        logger.info(
            "Updating video progress. "
            "User=%s Level=%s Seconds=%s",
            user["id"],
            level_id,
            watched_seconds,
        )

        progress = await self._get_or_create_progress(
            user["id"],
            level_id,
            course_id,
        )

        progress["video_watched_seconds"] = max(
            progress.get(
                "video_watched_seconds",
                0,
            ),
            watched_seconds,
        )

        if (
            progress["video_watched_seconds"]
            >= level.get(
                "video_duration_seconds",
                0,
            ) - 5
        ):
            progress["video_completed"] = True

        await self._save_progress(
            user["id"],
            level_id,
            progress,
        )

        logger.info(
            "Video progress updated. "
            "User=%s Level=%s",
            user["id"],
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
    ) -> dict:
        """Return existing progress or create a new document."""

        progress = (
            await self.progress_repository.get_by_user_and_level(
                user_id,
                level_id,
            )
        )

        if progress:
            return progress

        logger.info(
            "Creating progress document. User=%s Level=%s",
            user_id,
            level_id,
        )

        return LevelProgress(
            user_id=user_id,
            level_id=level_id,
            course_id=course_id,
        ).model_dump()

    async def _save_progress(
        self,
        user_id: str,
        level_id: str,
        progress: dict,
    ) -> None:
        """Persist student progress."""

        progress["updated_at"] = utc_now_iso()

        await self.progress_repository.save(
            user_id,
            level_id,
            progress,
        )

        logger.debug(
            "Progress saved. User=%s Level=%s",
            user_id,
            level_id,
        )

    async def _get_level(
        self,
        level_id: str,
    ) -> dict:
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
    ) -> list[dict]:
        """Return checkpoints for a level."""

        return (
            await self.challenge_repository.get_checkpoints_by_level(
                level_id,
            )
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
            user["id"],
            level_id,
        )

        level = await self._get_level(
            level_id,
        )

        progress = await self._validate_level_completion(
            level,
            user,
        )

        if progress.get(
            "completed",
            False,
        ):
            logger.info(
                "Level %s already completed by user %s",
                level_id,
                user["id"],
            )

            return {
                "ok": True,
                "xp_earned": 0,
            }

        xp_reward = int(
            level.get(
                "xp_reward",
                100,
            )
        )

        progress["completed"] = True
        progress["completed_at"] = utc_now_iso()

        progress["xp_earned"] = (
            progress.get(
                "xp_earned",
                0,
            )
            + xp_reward
        )

        await self._save_progress(
            user["id"],
            level_id,
            progress,
        )

        await self._award_xp(
            user["id"],
            xp_reward,
        )

        logger.info(
            "Level %s completed successfully by user %s. XP=%s",
            level_id,
            user["id"],
            xp_reward,
        )

        return {
            "ok": True,
            "xp_earned": xp_reward,
        }

    async def _validate_level_completion(
        self,
        level: dict,
        user: dict,
    ) -> dict:
        """Validate whether a level can be completed."""

        progress = (
            await self.progress_repository.get_by_user_and_level(
                user["id"],
                level["id"],
            )
        )

        if not progress:
            logger.warning(
                "No progress found. User=%s Level=%s",
                user["id"],
                level["id"],
            )

            raise BadRequestException(
                "No progress yet"
            )

        checkpoints = await self._get_checkpoints(
            level["id"],
        )

        required_checkpoint_ids = {
            checkpoint["id"]
            for checkpoint in checkpoints
        }

        completed_checkpoint_ids = {
            checkpoint["checkpoint_id"]
            for checkpoint in progress.get(
                "checkpoints",
                [],
            )
            if checkpoint.get(
                "completed",
                False,
            )
        }

        missing_checkpoint_ids = (
            required_checkpoint_ids
            - completed_checkpoint_ids
        )

        if missing_checkpoint_ids:
            logger.warning(
                "Checkpoint validation failed. "
                "User=%s Level=%s Missing=%s",
                user["id"],
                level["id"],
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
        progress: dict,
        level: dict,
    ) -> None:
        """Ensure the required video has been watched."""

        if progress.get(
            "video_completed",
            False,
        ):
            return

        watched_seconds = int(
            progress.get(
                "video_watched_seconds",
                0,
            )
        )

        video_duration = int(
            level.get(
                "video_duration_seconds",
                0,
            )
        )

        required_seconds = (
            video_duration * 0.85
        )

        if watched_seconds < required_seconds:
            logger.warning(
                "Video completion validation failed. "
                "Level=%s Watched=%s Required=%s",
                level["id"],
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
        """Award level XP and update the user's streak."""

        if xp <= 0:
            return

        await self.user_repository.increment_xp_and_streak(
            user_id,
            xp,
        )

        logger.info(
            "XP and streak updated. User=%s XP=%s",
            user_id,
            xp,
        )

    async def get_dashboard(
        self,
        user: dict,
    ) -> dict:
       """Return dashboard information for the logged-in user."""

       logger.info(
       "Loading dashboard for user %s",
        user["id"],
        )

       profile = await self.user_repository.get_public_by_id(
        user["id"],
        )

       if not profile:
        raise NotFoundException(
            "User not found",
        )

        enrollments = await self.course_repository.get_user_enrollments(
        user["id"],
    )

        progress = await self.progress_repository.get_by_user(
        user["id"],
    )

        completed_levels = await self.progress_repository.count_completed_levels(
        user_id=user["id"],
    )

        return {
        "user": profile,
        "enrollments": enrollments,
        "progress": progress,
        "completed_levels": completed_levels,
        "xp": profile.get("xp", 0),
        "streak": profile.get("streak_count", 0),
         }
progress_service = ProgressService()