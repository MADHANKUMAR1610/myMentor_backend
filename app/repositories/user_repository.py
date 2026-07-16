"""User database operations."""

import logging
from typing import Optional

from app.database import get_database

logger = logging.getLogger(__name__)

MAX_RESULTS = 500

DEFAULT_PROJECTION = {
    "_id": 0,
}

PUBLIC_USER_PROJECTION = {
    "_id": 0,
    "hashed_password": 0,
}


class UserRepository:
    """Repository for user collection operations."""

    @property
    def collection(self):
        """Return the users collection."""
        return get_database().users

    async def get_by_email(
        self,
        email: str,
    ) -> Optional[dict]:
        """Return a user by email."""

        logger.debug(
            "Fetching user by email %s",
            email,
        )

        return await self.collection.find_one(
            {
                "email": email,
            },
            DEFAULT_PROJECTION,
        )

    async def get_by_id(
        self,
        user_id: str,
    ) -> Optional[dict]:
        """Return a user by ID."""

        logger.debug(
            "Fetching user %s",
            user_id,
        )

        return await self.collection.find_one(
            {
                "id": user_id,
            },
            DEFAULT_PROJECTION,
        )

    async def get_public_by_id(
        self,
        user_id: str,
    ) -> Optional[dict]:
        """Return a user's public profile."""

        logger.debug(
            "Fetching public profile for user %s",
            user_id,
        )

        return await self.collection.find_one(
            {
                "id": user_id,
            },
            PUBLIC_USER_PROJECTION,
        )

    async def create(
        self,
        user: dict,
    ) -> None:
        """Insert a new user."""

        logger.debug(
            "Creating user %s",
            user["id"],
        )

        await self.collection.insert_one(
            user,
        )

    async def increment_xp(
        self,
        user_id: str,
        xp: int,
    ) -> None:
        """Increase a user's XP."""

        logger.debug(
            "Incrementing XP for user %s by %s",
            user_id,
            xp,
        )

        await self.collection.update_one(
            {
                "id": user_id,
            },
            {
                "$inc": {
                    "xp": xp,
                }
            },
        )

    async def increment_xp_and_streak(
        self,
        user_id: str,
        xp: int,
    ) -> None:
        """Increase a user's XP and streak."""

        logger.debug(
            "Incrementing XP and streak for user %s",
            user_id,
        )

        await self.collection.update_one(
            {
                "id": user_id,
            },
            {
                "$inc": {
                    "xp": xp,
                    "streak_count": 1,
                }
            },
        )

    async def count_students(self) -> int:
        """Return total student count."""

        logger.debug(
            "Counting students",
        )

        return await self.collection.count_documents(
            {
                "role": "student",
            }
        )

    async def get_students(self) -> list[dict]:
        """Return all students."""

        logger.debug(
            "Fetching student list",
        )

        return await self.collection.find(
            {
                "role": "student",
            },
            PUBLIC_USER_PROJECTION,
        ).to_list(MAX_RESULTS)

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
            await self.collection.find(
                {
                    "role": "student",
                },
                PUBLIC_USER_PROJECTION,
            )
            .sort("xp", -1)
            .limit(limit)
            .to_list(limit)
        )


user_repository = UserRepository()