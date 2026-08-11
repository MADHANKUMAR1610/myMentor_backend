"""OTP database operations."""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp_verification import OTPVerification

logger = logging.getLogger(__name__)


class OTPRepository:
    """Repository for OTP operations."""

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        otp: OTPVerification,
    ) -> None:
        """Save OTP."""

        print("OTP REPOSITORY CREATE", flush=True)

        logger.debug(
            "Saving OTP for %s",
            otp.mobile,
        )

        self.db.add(otp)

        await self.db.commit()

        await self.db.refresh(otp)

    async def get_valid_otp(
        self,
        mobile: str,
        otp: str,
    ) -> Optional[OTPVerification]:
        """Return valid OTP."""

        print(
            f"GET VALID OTP: {mobile}",
            flush=True,
        )

        result = await self.db.execute(
            select(OTPVerification).where(
                OTPVerification.mobile == mobile,
                OTPVerification.otp == otp,
                OTPVerification.verified.is_(False),
                OTPVerification.expires_at
                > datetime.utcnow(),
            )
        )

        return result.scalar_one_or_none()

    async def mark_verified(
        self,
        otp: OTPVerification,
    ) -> None:
        """Mark OTP as verified."""

        print(
            f"MARK OTP VERIFIED: {otp.mobile}",
            flush=True,
        )

        otp.verified = True

        await self.db.commit()

        await self.db.refresh(otp)

    async def delete_old_otps(
        self,
        mobile: str,
    ) -> None:
        """Delete previous OTPs."""

        print(
            f"DELETE OLD OTP: {mobile}",
            flush=True,
        )

        await self.db.execute(
            delete(OTPVerification).where(
                OTPVerification.mobile == mobile,
            )
        )

        await self.db.commit()