"""Career path database operations."""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_profile import CareerProfile
from app.models.career_report import CareerReport
from app.models.career_roadmap import CareerRoadmap

logger = logging.getLogger(__name__)


class CareerPathRepository:
    """Repository for career path operations."""

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # -----------------------------
    # Career Profile
    # -----------------------------

    async def get_profile_by_user_id(
        self,
        user_id: str,
    ) -> Optional[CareerProfile]:
        """Return career profile for a user."""

        logger.debug(
            "Fetching career profile for user %s",
            user_id,
        )

        result = await self.db.execute(
            select(CareerProfile).where(
                CareerProfile.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def create_profile(
        self,
        profile: CareerProfile,
    ) -> None:
        """Create career profile."""

        logger.debug(
            "Creating career profile %s",
            profile.id,
        )

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

    async def update_profile(
        self,
        profile: CareerProfile,
    ) -> None:
        """Update career profile."""

        logger.debug(
            "Updating career profile %s",
            profile.id,
        )

        await self.db.commit()
        await self.db.refresh(profile)

    # -----------------------------
    # Career Report
    # -----------------------------

    async def get_report_by_profile(
        self,
        profile_id: str,
    ) -> Optional[CareerReport]:
        """Return report for a profile."""

        logger.debug(
            "Fetching report for profile %s",
            profile_id,
        )

        result = await self.db.execute(
            select(CareerReport).where(
                CareerReport.profile_id == profile_id
            )
        )

        return result.scalar_one_or_none()

    async def create_report(
        self,
        report: CareerReport,
    ) -> None:
        """Create career report."""

        logger.debug(
            "Creating career report %s",
            report.id,
        )

        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

    async def update_report(
        self,
        report: CareerReport,
    ) -> None:
        """Update career report."""

        logger.debug(
            "Updating career report %s",
            report.id,
        )

        await self.db.commit()
        await self.db.refresh(report)

    # -----------------------------
    # Career Roadmap
    # -----------------------------

    async def get_roadmap(
        self,
        report_id: str,
    ) -> list[CareerRoadmap]:
        """Return roadmap for a report."""

        logger.debug(
            "Fetching roadmap for report %s",
            report_id,
        )

        result = await self.db.execute(
            select(CareerRoadmap)
            .where(
                CareerRoadmap.report_id == report_id
            )
            .order_by(
                CareerRoadmap.phase_number
            )
        )

        return result.scalars().all()

    async def create_roadmap(
        self,
        roadmap: list[CareerRoadmap],
    ) -> None:
        """Create roadmap."""

        logger.debug(
            "Creating %s roadmap phases",
            len(roadmap),
        )

        self.db.add_all(roadmap)
        await self.db.commit()

    async def delete_roadmap(
        self,
        report_id: str,
    ) -> None:
        """Delete roadmap."""

        roadmap = await self.get_roadmap(
            report_id,
        )

        for item in roadmap:
            await self.db.delete(item)

        await self.db.commit()

    # -----------------------------
    # Complete Career Data
    # -----------------------------

    async def get_complete_report(
        self,
        user_id: str,
    ) -> tuple[
        Optional[CareerProfile],
        Optional[CareerReport],
        list[CareerRoadmap],
    ]:
        """Return profile, report and roadmap."""

        profile = await self.get_profile_by_user_id(
            user_id,
        )

        if not profile:
            return None, None, []

        report = await self.get_report_by_profile(
            profile.id,
        )

        if not report:
            return profile, None, []

        roadmap = await self.get_roadmap(
            report.id,
        )

        return profile, report, roadmap
async def delete_report(
    self,
    report: CareerReport,
) -> None:
    """Delete career report."""

    logger.debug(
        "Deleting career report %s",
        report.id,
    )

    await self.db.delete(report)
    await self.db.commit()


async def replace_existing_report(
    self,
    profile_id: str,
) -> None:
    """
    Remove previous report and roadmap.
    """

    report = await self.get_report(
        profile_id,
    )

    if not report:
        return

    await self.delete_roadmap(
        report.id,
    )

    await self.delete_report(
        report,
    )
async def get_complete_report(
    self,
    user_id: str,
):
    """Return career profile, report and roadmap."""

    profile = await self.get_profile_by_user_id(
        user_id,
    )

    if not profile:
        return None, None, []

    report = await self.get_report_by_profile(
        profile.id,
    )

    if not report:
        return profile, None, []

    roadmap = await self.get_roadmap(
        report.id,
    )

    return profile, report, roadmap