"""Certificate generation business logic."""

import io
import logging
from datetime import datetime, timezone

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
)
from app.repositories import (
    course_repository,
    level_repository,
    progress_repository,
)

logger = logging.getLogger(__name__)


class CertificateService:
    """Validate course completion and generate certificates."""

    def __init__(self) -> None:
        self.course_repository = course_repository
        self.level_repository = level_repository
        self.progress_repository = progress_repository

    async def generate_certificate(
        self,
        course_id: str,
        user: dict,
    ) -> io.BytesIO:
        """Generate a certificate for a completed course."""

        logger.info(
            "Generating certificate for user %s and course %s",
            user["id"],
            course_id,
        )

        course = await self.course_repository.get_by_id(
            course_id
        )

        if not course:
            logger.warning(
                "Course not found: %s",
                course_id,
            )

            raise NotFoundException(
                "Course not found"
            )

        total_levels = (
            await self.level_repository.count_by_course(
                course_id
            )
        )

        completed_levels = (
            await self.progress_repository
            .count_completed_by_user_and_course(
                user["id"],
                course_id,
            )
        )

        if (
            total_levels == 0
            or completed_levels < total_levels
        ):
            logger.warning(
                "Certificate denied. User %s completed %s/%s levels.",
                user["id"],
                completed_levels,
                total_levels,
            )

            raise ForbiddenException(
                f"Course not completed ({completed_levels}/{total_levels} levels)"
            )

        buffer = self._create_pdf(
            user_name=user["name"],
            course_title=course["title"],
        )

        logger.info(
            "Certificate generated successfully for user %s",
            user["id"],
        )

        return buffer

    def _create_pdf(
        self,
        user_name: str,
        course_title: str,
    ) -> io.BytesIO:
        """Create the certificate PDF."""

        buffer = io.BytesIO()

        width, height = landscape(A4)

        pdf = canvas.Canvas(
            buffer,
            pagesize=landscape(A4),
        )

        pdf.setFillColorRGB(
            0.035,
            0.035,
            0.043,
        )
        pdf.rect(
            0,
            0,
            width,
            height,
            fill=1,
            stroke=0,
        )

        pdf.setStrokeColorRGB(
            0.23,
            0.51,
            0.96,
        )
        pdf.setLineWidth(3)
        pdf.rect(
            30,
            30,
            width - 60,
            height - 60,
            fill=0,
        )

        pdf.setFillColorRGB(
            1,
            1,
            1,
        )

        pdf.setFont(
            "Helvetica-Bold",
            42,
        )
        pdf.drawCentredString(
            width / 2,
            height - 130,
            "Certificate of Completion",
        )

        pdf.setFont(
            "Helvetica",
            18,
        )
        pdf.setFillColorRGB(
            0.63,
            0.63,
            0.70,
        )
        pdf.drawCentredString(
            width / 2,
            height - 170,
            "DIGIPIN ACADEMY",
        )

        pdf.setFillColorRGB(
            1,
            1,
            1,
        )

        pdf.setFont(
            "Helvetica-Bold",
            36,
        )
        pdf.drawCentredString(
            width / 2,
            height - 260,
            user_name,
        )

        pdf.setFont(
            "Helvetica",
            16,
        )
        pdf.setFillColorRGB(
            0.85,
            0.85,
            0.88,
        )
        pdf.drawCentredString(
            width / 2,
            height - 300,
            "has successfully completed the course",
        )

        pdf.setFont(
            "Helvetica-Bold",
            22,
        )
        pdf.setFillColorRGB(
            0.23,
            0.51,
            0.96,
        )
        pdf.drawCentredString(
            width / 2,
            height - 340,
            course_title,
        )

        pdf.setFillColorRGB(
            0.63,
            0.63,
            0.70,
        )
        pdf.setFont(
            "Helvetica",
            12,
        )

        issued_date = datetime.now(
            timezone.utc
        ).strftime("%B %d, %Y")

        pdf.drawString(
            70,
            70,
            f"Issued: {issued_date}",
        )

        pdf.drawRightString(
            width - 70,
            70,
            "Digipin Academy · https://digipin.academy",
        )

        pdf.showPage()
        pdf.save()

        buffer.seek(0)

        return buffer


certificate_service = CertificateService()