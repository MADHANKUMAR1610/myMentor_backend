"""OTP service."""

import random
from datetime import datetime, timedelta
from uuid import uuid4

import requests

from app.core.config import settings
from app.models.otp_verification import OTPVerification
from app.repositories.otp_repository import OTPRepository
from app.repositories.user_repository import UserRepository


class OTPService:
    """OTP business logic."""

    def __init__(
        self,
        repository: OTPRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.user_repository = user_repository

    def _send_sms(
        self,
        mobile: str,
        otp: str,
    ) -> None:
        """Send OTP SMS using SmsHorizon."""

        print(
            "========================================",
            flush=True,
        )

        print(
            "SMS HORIZON SMS FUNCTION HIT",
            flush=True,
        )

        # --------------------------------------------------
        # Check configuration
        # --------------------------------------------------

        api_key = (
            settings.SMSHORIZON_API_KEY
            .get_secret_value()
        )

        if not api_key:
            raise RuntimeError(
                "SMSHORIZON_API_KEY is missing."
            )

        if not settings.SMSHORIZON_USER:
            raise RuntimeError(
                "SMSHORIZON_USER is missing."
            )

        if not settings.SMSHORIZON_SENDER_ID:
            raise RuntimeError(
                "SMSHORIZON_SENDER_ID is missing."
            )

        # --------------------------------------------------
        # URL
        # --------------------------------------------------

        url = (
            f"{settings.SMSHORIZON_BASE_URL}"
            "/sendsms"
        )

        # --------------------------------------------------
        # Headers
        # --------------------------------------------------

        headers = {
            "Authorization": (
                f"Bearer {api_key}"
            ),
        }

        # --------------------------------------------------
        # Request data
        # --------------------------------------------------

        data = {
            "user": settings.SMSHORIZON_USER,
            "number": mobile,
            "message": (
                f"Your Digipin Academy OTP is {otp}. "
                "It is valid for 5 minutes."
            ),
            "senderid": (
                settings.SMSHORIZON_SENDER_ID
            ),
            "type": "txt",
        }

        # Add template only when available
        if settings.SMSHORIZON_TEMPLATE_ID:
            data["tid"] = (
                settings.SMSHORIZON_TEMPLATE_ID
            )

        # --------------------------------------------------
        # Debug information
        # --------------------------------------------------

        print(
            f"SmsHorizon URL: {url}",
            flush=True,
        )

        print(
            f"SmsHorizon USER: "
            f"{settings.SMSHORIZON_USER}",
            flush=True,
        )

        print(
            f"SmsHorizon NUMBER: {mobile}",
            flush=True,
        )

        print(
            f"SmsHorizon SENDER ID: "
            f"{settings.SMSHORIZON_SENDER_ID}",
            flush=True,
        )

        print(
            "SmsHorizon API KEY: configured",
            flush=True,
        )

        print(
            "Sending SMS request...",
            flush=True,
        )

        # --------------------------------------------------
        # Send request
        # --------------------------------------------------

        try:

            response = requests.post(
                url,
                headers=headers,
                data=data,
                timeout=30,
            )

        except requests.RequestException as exc:

            print(
                "SMSHORIZON CONNECTION ERROR",
                flush=True,
            )

            print(
                str(exc),
                flush=True,
            )

            raise RuntimeError(
                "Could not connect to SmsHorizon."
            ) from exc

        # --------------------------------------------------
        # Print provider response
        # --------------------------------------------------

        print(
            "========== SMSHORIZON RESPONSE ==========",
            flush=True,
        )

        print(
            f"HTTP STATUS: {response.status_code}",
            flush=True,
        )

        print(
            f"RESPONSE: {response.text}",
            flush=True,
        )

        print(
            "==========================================",
            flush=True,
        )

        # --------------------------------------------------
        # Provider rejected request
        # --------------------------------------------------

        if response.status_code >= 400:

            raise RuntimeError(
                "SmsHorizon rejected the SMS request. "
                f"Status: {response.status_code}. "
                f"Response: {response.text}"
            )

        # --------------------------------------------------
        # Provider accepted request
        # --------------------------------------------------

        print(
            "SMS REQUEST ACCEPTED BY SMSHORIZON",
            flush=True,
        )

    async def send_otp(
        self,
        mobile: str,
    ) -> str:
        """Generate, save and send OTP."""

        print(
            "========================================",
            flush=True,
        )

        print(
            f"OTP SERVICE HIT: {mobile}",
            flush=True,
        )

        # --------------------------------------------------
        # Check registered mobile
        # --------------------------------------------------

        user = (
            await self.user_repository.get_by_mobile(
                self.repository.db,
                mobile,
            )
        )

        if user is None:

            print(
                f"Mobile not registered: {mobile}",
                flush=True,
            )

            raise ValueError(
                "Mobile number is not registered."
            )

        print(
            f"Registered user found: {user.id}",
            flush=True,
        )

        # --------------------------------------------------
        # Generate OTP
        # --------------------------------------------------

        otp = str(
            random.randint(
                100000,
                999999,
            )
        )

        print(
            "OTP generated",
            flush=True,
        )

        # --------------------------------------------------
        # Delete previous OTP
        # --------------------------------------------------

        await self.repository.delete_old_otps(
            mobile,
        )

        # --------------------------------------------------
        # Create OTP record
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Save OTP
        # --------------------------------------------------

        await self.repository.create(
            otp_model,
        )

        print(
            "OTP saved to database",
            flush=True,
        )

        # --------------------------------------------------
        # Send SMS
        # --------------------------------------------------

        try:

            self._send_sms(
                mobile,
                otp,
            )

        except Exception as exc:

            print(
                "SMS SENDING FAILED",
                flush=True,
            )

            print(
                str(exc),
                flush=True,
            )

            # IMPORTANT:
            # Do not tell frontend that SMS was sent.
            raise

        print(
            "OTP SENT SUCCESSFULLY",
            flush=True,
        )

        print(
            "========================================",
            flush=True,
        )

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

            print(
                "Invalid or expired OTP",
                flush=True,
            )

            return False

        await self.repository.mark_verified(
            otp_model,
        )

        print(
            "OTP VERIFIED SUCCESSFULLY",
            flush=True,
        )

        return True