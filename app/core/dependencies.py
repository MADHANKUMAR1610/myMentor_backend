"""Application dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.repositories.otp_repository import OTPRepository
from app.repositories.user_repository import UserRepository
from app.services.otp_service import OTPService


def get_otp_service(
    db: AsyncSession = Depends(get_db),
) -> OTPService:
    """Create OTP service."""

    otp_repository = OTPRepository(
        db
    )

    user_repository = UserRepository()

    return OTPService(
        repository=otp_repository,
        user_repository=user_repository,
    )