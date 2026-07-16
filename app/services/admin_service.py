"""Admin reporting business logic."""

import logging
from datetime import (
    datetime,
    timedelta,
    timezone,
)

from app.repositories import admin_repository

logger = logging.getLogger(__name__)


class AdminService:
    """Handle admin dashboard and student reporting."""

    def __init__(self) -> None:
        self.admin_repository = admin_repository

    async def get_stats(self) -> dict:
        """Return admin dashboard statistics."""

        logger.info("Generating admin dashboard statistics")

        total_students = (
            await self.admin_repository.count_students()
        )

        total_courses = (
            await self.admin_repository.count_courses()
        )

        total_levels = (
            await self.admin_repository.count_levels()
        )

        total_challenges = (
            await self.admin_repository.count_challenges()
        )

        completed_levels = (
            await self.admin_repository.count_completed_levels()
        )

        total_submissions = (
            await self.admin_repository.count_submissions()
        )

        week_ago = (
            datetime.now(timezone.utc)
            - timedelta(days=7)
        ).isoformat()

        active_students = (
            await self.admin_repository.get_active_student_ids(
                week_ago
            )
        )

        stats = {
            "total_students": total_students,
            "active_students": len(active_students),
            "total_courses": total_courses,
            "total_levels": total_levels,
            "total_challenges": total_challenges,
            "completed_levels": completed_levels,
            "total_submissions": total_submissions,
            "learning_hours": total_submissions * 5 // 60,
        }

        logger.info(
            "Dashboard statistics generated successfully."
        )

        return stats

    async def get_students(self) -> list[dict]:
        """Return all students with completed level count."""

        logger.info("Generating student report")

        students = (
            await self.admin_repository.get_students()
        )

        for student in students:
            student["completed_levels"] = (
                await self.admin_repository.count_completed_levels_for_user(
                    student["id"]
                )
            )

        logger.info(
            "Student report generated. Total students: %s",
            len(students),
        )

        return students

    async def get_leaderboard(self) -> list[dict]:
        """Return leaderboard."""

        logger.info("Generating leaderboard")

        leaderboard = (
            await self.admin_repository.get_leaderboard(
                limit=20,
            )
        )

        logger.info(
            "Leaderboard generated successfully. Entries: %s",
            len(leaderboard),
        )

        return leaderboard


admin_service = AdminService()