"""Career path business logic."""

import logging
from uuid import uuid4

from app.models.career_profile import CareerProfile
from app.models.career_report import CareerReport
from app.models.career_roadmap import CareerRoadmap
from app.repositories.career_path_repository import CareerPathRepository
from app.schemas.career_path import (
    CareerProfileCreate,
    CareerProfileResponse,
)
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class CareerPathService:
    """Career Path business logic."""

    def __init__(
        self,
        repository: CareerPathRepository,
    ):
        self.repository = repository

    async def save_profile(
        self,
        payload: CareerProfileCreate,
        current_user,
    ) -> CareerProfileResponse:
        """Create or update career profile."""

        logger.info(
            "Saving career profile for user %s",
            current_user.id,
        )

        profile = await self.repository.get_profile_by_user_id(
            current_user.id,
        )

        if profile:

            profile.career_goal = payload.career_goal
            profile.full_name = payload.full_name
            profile.date_of_birth = payload.date_of_birth
            profile.education_stage = payload.education_stage

            await self.repository.update_profile(
                profile,
            )

            return CareerProfileResponse.model_validate(
                profile,
            )

        profile = CareerProfile(
            id=str(uuid4()),
            user_id=current_user.id,
            career_goal=payload.career_goal,
            full_name=payload.full_name,
            date_of_birth=payload.date_of_birth,
            education_stage=payload.education_stage,
        )

        await self.repository.create_profile(
            profile,
        )

        return CareerProfileResponse.model_validate(
            profile,
        )

    async def generate_report(
        self,
        current_user,
    ):
        """Generate AI career report."""

        logger.info(
            "Generating career report for user %s",
            current_user.id,
        )

        profile = await self.repository.get_profile_by_user_id(
            current_user.id,
        )

        if not profile:
            raise Exception(
                "Career profile not found."
            )

        # Delete previous report & roadmap (Explore Another Path)
        await self.repository.replace_existing_report(
            profile.id,
        )

        # Generate AI response
        report_data = await gemini_service.generate_career_report(
            career_goal=profile.career_goal,
            full_name=profile.full_name,
            education_stage=profile.education_stage,
            date_of_birth=str(
                profile.date_of_birth,
            ),
        )

        # Save report
        report = CareerReport(
            id=str(uuid4()),
            profile_id=profile.id,
            career_persona=report_data["career_persona"],
            confidence_score=report_data["confidence_score"],
            recommended_stream=report_data["recommended_stream"],
            primary_skill=report_data["primary_skill"],
            career_overview=report_data["career_overview"],
            next_step=report_data["next_step"],
            target_exams=report_data["target_exams"],
        )

        await self.repository.create_report(
            report,
        )

        # Save roadmap
        roadmap = []

        for item in report_data["roadmap"]:

            roadmap.append(
                CareerRoadmap(
                    id=str(uuid4()),
                    report_id=report.id,
                    phase_number=item["phase_number"],
                    phase_title=item["phase_title"],
                    duration=item["duration"],
                    description=item["description"],
                )
            )

        await self.repository.create_roadmap(
            roadmap,
        )

        logger.info(
            "Career report generated successfully."
        )

        return report_data
    async def get_profile(
        self,
        current_user,
    ):
        """Return saved career profile."""

        profile = await self.repository.get_profile_by_user_id(
        current_user.id,
        )

        if not profile:
          raise Exception(
            "Career profile not found."
        )

        return CareerProfileResponse.model_validate(
        profile,
    )
    
    async def get_report(
        self,
        current_user,
):
        """Return saved career report."""

        profile, report, roadmap = (
        await self.repository.get_complete_report(
            current_user.id,
        )
    )

        if not profile:
          raise Exception(
            "Career profile not found."
        )

        if not report:
          raise Exception(
            "Career report not found."
        )

        return {
        "career_persona": report.career_persona,
        "confidence_score": report.confidence_score,
        "recommended_stream": report.recommended_stream,
        "primary_skill": report.primary_skill,
        "career_overview": report.career_overview,
        "next_step": report.next_step,
        "target_exams": report.target_exams,
        "roadmap": [
            {
                "phase_number": item.phase_number,
                "phase_title": item.phase_title,
                "duration": item.duration,
                "description": item.description,
            }
            for item in roadmap
        ],
    }