"""Career path business logic."""

import logging

from app.services.gemini_service import gemini_service
from app.models.career_report import CareerReport
from app.models.career_roadmap import CareerRoadmap
from app.repositories.career_path_repository import CareerPathRepository

logger = logging.getLogger(__name__)


class CareerPathService:
    """Career path business logic."""

    def __init__(
        self,
        repository: CareerPathRepository,
    ):
        self.repository = repository

    async def generate_report(
        self,
        current_user,
    ):
        """Generate AI career report."""

        profile = await self.repository.get_profile_by_user_id(
            current_user.id,
        )

        if not profile:
            raise Exception(
                "Career profile not found."
            )

        report_data = (
            await gemini_service.generate_career_report(
                career_goal=profile.career_goal,
                full_name=profile.full_name,
                education_stage=profile.education_stage,
                date_of_birth=str(
                    profile.date_of_birth,
                ),
            )
        )

        report = CareerReport(
            profile_id=profile.id,
            career_persona=report_data[
                "career_persona"
            ],
            confidence_score=report_data[
                "confidence_score"
            ],
            recommended_stream=report_data[
                "recommended_stream"
            ],
            primary_skill=report_data[
                "primary_skill"
            ],
            career_overview=report_data[
                "career_overview"
            ],
            next_step=report_data[
                "next_step"
            ],
            target_exams=report_data[
                "target_exams"
            ],
        )

        await self.repository.create_report(
            report,
        )

        roadmap = []

        for item in report_data[
            "roadmap"
        ]:

            roadmap.append(
                CareerRoadmap(
                    report_id=report.id,
                    phase_number=item[
                        "phase_number"
                    ],
                    phase_title=item[
                        "phase_title"
                    ],
                    duration=item[
                        "duration"
                    ],
                    description=item[
                        "description"
                    ],
                )
            )

        await self.repository.create_roadmap(
            roadmap,
        )

        return report_data