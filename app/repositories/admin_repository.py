"""Admin dashboard database operations."""

import logging

from app.database import get_database

logger = logging.getLogger(__name__)

MAX_RESULTS = 500

USER_PUBLIC_PROJECTION = {
    "_id": 0,
    "hashed_password": 0,
}


class AdminRepository:
    """Repository for admin reporting operations."""

    @property
    def user_collection(self):
        return get_database().users

    @property
    def course_collection(self):
        return get_database().courses

    @property
    def level_collection(self):
        return get_database().levels

    @property
    def challenge_collection(self):
        return get_database().challenges

    @property
    def progress_collection(self):
        return get_database().progress

    @property
    def submission_collection(self):
        return get_database().submissions

    async def count_students(self) -> int:
        """Return total student count."""

        logger.debug("Counting students")

        return await self.user_collection.count_documents(
            {"role": "student"}
        )

    async def count_courses(self) -> int:
        """Return total course count."""

        logger.debug("Counting courses")

        return await self.course_collection.count_documents(
            {}
        )

    async def count_levels(self) -> int:
        """Return total level count."""

        logger.debug("Counting levels")

        return await self.level_collection.count_documents(
            {}
        )

    async def count_challenges(self) -> int:
        """Return total challenge count."""

        logger.debug("Counting challenges")

        return await self.challenge_collection.count_documents(
            {}
        )

    async def count_completed_levels(self) -> int:
        """Return total completed level count."""

        logger.debug("Counting completed levels")

        return await self.progress_collection.count_documents(
            {"completed": True}
        )

    async def count_submissions(self) -> int:
        """Return total submission count."""

        logger.debug("Counting submissions")

        return await self.submission_collection.count_documents(
            {}
        )

    async def get_active_student_ids(
        self,
        updated_since: str,
    ) -> list[str]:
        """Return IDs of students active since the given date."""

        logger.debug(
            "Fetching active students since %s",
            updated_since,
        )

        return await self.progress_collection.distinct(
            "user_id",
            {
                "updated_at": {
                    "$gte": updated_since,
                }
            },
        )

    async def get_students(self) -> list[dict]:
        """Return all students."""

        logger.debug("Fetching student list")

        return await self.user_collection.find(
            {"role": "student"},
            USER_PUBLIC_PROJECTION,
        ).to_list(MAX_RESULTS)

    async def count_completed_levels_for_user(
        self,
        user_id: str,
    ) -> int:
        """Return completed level count for a user."""

        logger.debug(
            "Counting completed levels for user %s",
            user_id,
        )

        return await self.progress_collection.count_documents(
            {
                "user_id": user_id,
                "completed": True,
            }
        )

    async def get_leaderboard(
        self,
        limit: int = 20,
    ) -> list[dict]:
        """Return leaderboard ordered by XP."""

        logger.debug(
            "Fetching leaderboard (limit=%s)",
            limit,
        )

        return (
            await self.user_collection.find(
                {"role": "student"},
                USER_PUBLIC_PROJECTION,
            )
            .sort("xp", -1)
            .limit(limit)
            .to_list(limit)
        )


admin_repository = AdminRepository()