"""Certificate API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from fastapi.responses import StreamingResponse

from app.core.auth import get_current_user
from app.services import certificate_service


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
    current_user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """Download a course completion certificate."""

    certificate_buffer = (
        await certificate_service.generate_certificate(
            course_id,
            current_user,
        )
    )

    return StreamingResponse(
        certificate_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="digipin-certificate-{course_id}.pdf"'
            )
        },
    )