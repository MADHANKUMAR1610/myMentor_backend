"""OTP service."""

import random
from datetime import datetime, timedelta
from uuid import uuid4

from twilio.rest import Client

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

    def _send_sms(
        self,
        mobile: str,
        otp: str,
    ) -> None:
        """Send OTP SMS using Twilio."""

        print("TWILIO SMS FUNCTION HIT", flush=True)

        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN.get_secret_value(),
        )

        message = client.messages.create(
            body=(
                f"Your Digipin Academy OTP is {otp}. "
                "It is valid for 5 minutes."
            ),
            from_=settings.TWILIO_PHONE_NUMBER,
            to=mobile,
        )

        print(
            f"Twilio SMS sent successfully: {message.sid}",
            flush=True,
        )

    async def send_otp(
        self,
        mobile: str,
    ) -> str:
        """Generate, save and send OTP."""

        print("OTP SERVICE HIT", flush=True)

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
        self._send_sms(
            mobile,
            otp,
        )

        # IMPORTANT:
        # Do not return the actual OTP.
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

        otp_model = await self.repository.get_valid_otp(
            mobile,
            otp,
        )

        if otp_model is None:
            return False

        await self.repository.mark_verified(
            otp_model,
        )

        return True