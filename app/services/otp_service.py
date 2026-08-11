"""OTP service."""

import random
from datetime import datetime, timedelta
from uuid import uuid4

import httpx

from app.core.config import settings
from app.models.otp_verification import OTPVerification
from app.repositories.otp_repository import OTPRepository


class OTPService:
    """OTP business logic."""

    def __init__(
        self,
        repository: OTPRepository,
    ):
        self.repository = repository

    async def _send_sms(
        self,
        mobile: str,
        otp: str,
    ) -> None:
        """Send OTP SMS using SmsHorizon."""

        print(
            "SMSHORIZON SMS FUNCTION HIT",
            flush=True,
        )

        url = (
            f"{settings.SMSHORIZON_BASE_URL}"
            "/sendsms"
        )

        headers = {
            "Authorization": (
                "Bearer "
                f"{settings.SMSHORIZON_API_KEY.get_secret_value()}"
            )
        }

        data = {
            "user": settings.SMSHORIZON_USER,
            "number": mobile,
            "message": (
                f"OTP for your new user account "
                f"registration is: {otp}"
            ),
            "type": "txt",
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                url,
                headers=headers,
                data=data,
            )

        print(
            "SmsHorizon status:",
            response.status_code,
            flush=True,
        )

        print(
            "SmsHorizon response:",
            response.text,
            flush=True,
        )

        if response.status_code >= 400:
            raise RuntimeError(
                "SmsHorizon SMS sending failed: "
                f"{response.text}"
            )

    async def send_otp(
        self,
        mobile: str,
    ) -> str:
        """Generate, save and send OTP."""

        print(
            "OTP SERVICE HIT",
            flush=True,
        )

        # Generate 6 digit OTP
        otp = str(
            random.randint(
                100000,
                999999,
            )
        )

        print(
            f"OTP generated for {mobile}",
            flush=True,
        )

        # Delete previous OTP
        await self.repository.delete_old_otps(
            mobile,
        )

        # Create OTP record
        otp_model = OTPVerification(
            id=str(uuid4()),
            mobile=mobile,
            otp=otp,
            verified=False,
            expires_at=(
                datetime.utcnow()
                + timedelta(minutes=5)
            ),
        )

        # Save OTP to PostgreSQL
        await self.repository.create(
            otp_model,
        )

        # Send SMS
        await self._send_sms(
            mobile,
            otp,
        )

        # Never return actual OTP
        return "OTP sent successfully"

    async def verify_otp(
        self,
        mobile: str,
        otp: str,
    ) -> bool:
        """Verify OTP."""

        print(
            f"VERIFY OTP HIT: {mobile}",
            flush=True,
        )

        otp_model = (
            await self.repository.get_valid_otp(
                mobile,
                otp,
            )
        )

        if otp_model is None:
            return False

        await self.repository.mark_verified(
            otp_model,
        )

        return True