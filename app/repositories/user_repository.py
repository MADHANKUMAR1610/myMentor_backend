"""User database operations using PostgreSQL."""

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

logger = logging.getLogger(__name__)

MAX_RESULTS = 500


class UserRepository:
    """Repository for user table operations."""

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> Optional[User]:
        logger.debug("Fetching user by email %s", email)

        result = await db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Optional[User]:
        logger.debug("Fetching user %s", user_id)

        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    async def get_public_by_id(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Optional[User]:
        logger.debug(
            "Fetching public profile for user %s",
            user_id,
        )

        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        user: User,
    ) -> None:
        logger.debug("Creating user %s", user.id)

        db.add(user)
        await db.commit()
        await db.refresh(user)

    async def update(
        self,
        db: AsyncSession,
        user: User,
    ) -> User:
        logger.debug("Updating user %s", user.id)

        await db.commit()
        await db.refresh(user)

        return user

    async def get_by_mobile(
        self,
        db: AsyncSession,
        mobile: str,
    ) -> User | None:
        """Return user by mobile number."""

        result = await db.execute(
            select(User).where(
                User.mobile == mobile
            )
        )

        return result.scalar_one_or_none()

    async def get_by_google_id(
        self,
        db: AsyncSession,
        google_id: str,
    ) -> User | None:
        """Return user by Google ID."""

        result = await db.execute(
            select(User).where(
                User.google_id == google_id
            )
        )

        return result.scalar_one_or_none()

    async def increment_xp(
        self,
        db: AsyncSession,
        user_id: str,
        xp: int,
    ) -> None:
        logger.debug(
            "Incrementing XP for user %s by %s",
            user_id,
            xp,
        )

        user = await self.get_by_id(
            db,
            user_id,
        )

        if user:
            user.xp += xp
            await db.commit()

    async def increment_xp_and_streak(
        self,
        db: AsyncSession,
        user_id: str,
        xp: int,
    ) -> None:
        logger.debug(
            "Incrementing XP and streak for user %s",
            user_id,
        )

        user = await self.get_by_id(
            db,
            user_id,
        )

        if user:
            user.xp += xp
            user.streak_count += 1
            await db.commit()

    async def count_students(
        self,
        db: AsyncSession,
    ) -> int:
        logger.debug("Counting students")

        result = await db.execute(
            select(func.count())
            .select_from(User)
            .where(User.role == "student")
        )

        return result.scalar_one()

    async def get_students(
        self,
        db: AsyncSession,
    ) -> list[User]:
        logger.debug("Fetching student list")

        result = await db.execute(
            select(User)
            .where(User.role == "student")
            .limit(MAX_RESULTS)
        )

        return list(result.scalars().all())

    async def get_leaderboard(
        self,
        db: AsyncSession,
        limit: int = 20,
    ) -> list[User]:
        logger.debug(
            "Fetching leaderboard (limit=%s)",
            limit,
        )

        result = await db.execute(
            select(User)
            .where(User.role == "student")
            .order_by(User.xp.desc())
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_leaderboard_summary(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> dict:
        """Return leaderboard summary."""

        logger.debug(
            "Fetching leaderboard summary for user %s",
            user_id,
        )

        leaderboard = await self.get_leaderboard(
            db,
            limit=100,
        )

        rank = None

        for index, user in enumerate(
            leaderboard,
            start=1,
        ):
            if user.id == user_id:
                rank = index
                break

        return {
            "rank": rank,
            "total_students": len(leaderboard),
        }


user_repository = UserRepository()