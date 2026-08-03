"""Admin reporting business logic."""

import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.level_repository import LevelRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AdminService:
    """Handle admin dashboard and reporting."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository()
        self.course_repository = CourseRepository(db)
        self.level_repository = LevelRepository(db)
        self.challenge_repository = ChallengeRepository(db)
        self.progress_repository = ProgressRepository(db)

    async def get_stats(self) -> dict:
        """Return admin dashboard statistics."""

        logger.info("Generating admin dashboard")

        total_students = await self.user_repository.count_students(self.db)

        total_courses = await self.course_repository.count_courses()

        total_levels = await self.level_repository.count_levels()

        total_challenges = await self.challenge_repository.count_challenges()

        completed_levels = (
            await self.progress_repository.count_completed_levels()
        )

        total_submissions = (
            await self.progress_repository.count_submissions()
        )

        week_ago = datetime.utcnow() - timedelta(days=7)

        active_students = (
            await self.progress_repository.get_active_user_ids_since(
                week_ago
            )
        )

        return {
            "total_students": total_students,
            "active_students": len(active_students),
            "total_courses": total_courses,
            "total_levels": total_levels,
            "total_challenges": total_challenges,
            "completed_levels": completed_levels,
            "total_submissions": total_submissions,
            "learning_hours": total_submissions * 5 // 60,
        }

    async def get_students(self):
        """Return all students."""

        students = await self.user_repository.get_students(self.db)

        result = []

        for student in students:
            completed = (
                await self.progress_repository
                .count_completed_by_user_and_course(
                    student.id,
                    "",
                )
            )

            result.append(
                {
                    "id": student.id,
                    "name": student.name,
                    "email": student.email,
                    "xp": student.xp,
                    "streak_count": student.streak_count,
                    "completed_levels": completed,
                }
            )

        return result

    async def get_leaderboard(self):
        """Return leaderboard."""

        students = await self.user_repository.get_leaderboard(
            self.db,
            limit=20,
        )

        leaderboard = []

        rank = 1

        for student in students:
            leaderboard.append(
                {
                    "rank": rank,
                    "id": student.id,
                    "name": student.name,
                    "xp": student.xp,
                    "streak_count": student.streak_count,
                }
            )

            rank += 1

        return leaderboard