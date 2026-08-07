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

    # ==========================================================
    # Career Profile
    # ==========================================================

    async def get_profile_by_user_id(
        self,
        user_id: str,
    ) -> Optional[CareerProfile]:

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

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

    async def update_profile(
        self,
        profile: CareerProfile,
    ) -> None:

        await self.db.commit()
        await self.db.refresh(profile)

    # ==========================================================
    # Career Report
    # ==========================================================

    async def get_report_by_profile(
        self,
        profile_id: str,
    ) -> Optional[CareerReport]:

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

        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

    async def update_report(
        self,
        report: CareerReport,
    ) -> None:

        await self.db.commit()
        await self.db.refresh(report)

    async def delete_report(
        self,
        report: CareerReport,
    ) -> None:

        await self.db.delete(report)
        await self.db.commit()

    # ==========================================================
    # Career Roadmap
    # ==========================================================

    async def get_roadmap(
        self,
        report_id: str,
    ) -> list[CareerRoadmap]:

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

        self.db.add_all(roadmap)
        await self.db.commit()

    async def delete_roadmap(
        self,
        report_id: str,
    ) -> None:

        roadmap = await self.get_roadmap(
            report_id,
        )

        for item in roadmap:
            await self.db.delete(item)

        await self.db.commit()

    # ==========================================================
    # Explore Another Path
    # ==========================================================

    async def replace_existing_report(
        self,
        profile_id: str,
    ) -> None:
        """
        Delete previous report and roadmap.
        """

        report = await self.get_report_by_profile(
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

    # ==========================================================
    # Get Complete Career Data
    # ==========================================================

    async def get_complete_report(
        self,
        user_id: str,
    ) -> tuple[
        Optional[CareerProfile],
        Optional[CareerReport],
        list[CareerRoadmap],
    ]:

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

        return (
            profile,
            report,
            roadmap,
        )