"""Certificate API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database.postgres import get_db
from app.services.certificate_service import CertificateService


router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"],
)


@router.get(
    "/{course_id}",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Download course certificate",
    description=(
        "Generate and download a PDF certificate after "
        "successfully completing a course."
    ),
    responses={
        200: {
            "description": "Certificate PDF",
            "content": {
                "application/pdf": {},
            },
        },
        403: {
            "description": "Course not completed",
        },
        404: {
            "description": "Course not found",
        },
    },
)
async def download_certificate(
    course_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Download a course completion certificate."""

    service = CertificateService(db)

    certificate_buffer = await service.generate_certificate(
        course_id,
        current_user,
    )

    return StreamingResponse(
        certificate_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="digipin-certificate-{course_id}.pdf"'
        },
    )