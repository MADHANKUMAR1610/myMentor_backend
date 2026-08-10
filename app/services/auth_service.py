"""Authentication business logic."""

import logging

from google.oauth2 import id_token

from google.auth.transport import requests

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from app.core.auth import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.core.exceptions import (
    BadRequestException,
    UnauthorizedException,
)

from app.models.user import User

from app.repositories.user_repository import user_repository
from app.repositories.otp_repository import OTPRepository

from app.services.otp_service import OTPService

from app.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserPublic,
    gen_id,
)


logger = logging.getLogger(__name__)


class AuthService:
    """Handle authentication and user registration."""

    def __init__(self):
        self.user_repository = user_repository

    def _build_public_user(
        self,
        user: User,
    ) -> UserPublic:
        return UserPublic(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            xp=user.xp,
            streak_count=user.streak_count,
            avatar_url=user.avatar_url,
        )

    async def register(
        self,
        db: AsyncSession,
        payload: UserCreate,
    ) -> TokenResponse:

        logger.info(
            "Registration attempt for %s",
            payload.email,
        )

        existing_user = await self.user_repository.get_by_email(
            db,
            payload.email,
        )

        if existing_user:
            raise BadRequestException(
                "Email already registered"
            )

        user = User(
            id=gen_id(),
            email=payload.email,
            hashed_password=hash_password(
                payload.password
            ),
            name=payload.name,
            role=payload.role,
            xp=0,
            streak_count=0,
            avatar_url=None,
            mobile=None,
            google_id=None,
            profile_image=None,
            login_provider="email",
            is_mobile_verified=False,
            is_email_verified=True,
        )

        await self.user_repository.create(
            db,
            user,
        )

        access_token = create_access_token(
            {
                "sub": user.id,
                "role": user.role,
            }
        )

        return TokenResponse(
            access_token=access_token,
            user=self._build_public_user(user),
        )

    async def login(
        self,
        db: AsyncSession,
        payload: LoginRequest,
    ) -> TokenResponse:

        logger.info(
            "Login attempt for %s",
            payload.email,
        )

        user = await self.user_repository.get_by_email(
            db,
            payload.email,
        )

        if (
            user is None
            or not verify_password(
                payload.password,
                user.hashed_password,
            )
        ):
            raise UnauthorizedException(
                "Invalid credentials"
            )

        access_token = create_access_token(
            {
                "sub": user.id,
                "role": user.role,
            }
        )

        return TokenResponse(
            access_token=access_token,
            user=self._build_public_user(user),
        )

    def get_current_user_response(
        self,
        user: User,
    ) -> UserPublic:

        return self._build_public_user(user)

    async def send_otp(
        self,
        db: AsyncSession,
        mobile: str,
    ):
        """Send OTP to student's mobile."""

        print("AUTH SERVICE HIT", flush=True)

        otp_repository = OTPRepository(db)
        otp_service = OTPService(otp_repository)

        return await otp_service.send_otp(mobile)

    async def verify_otp(
        self,
        db: AsyncSession,
        mobile: str,
        otp: str,
    ) -> TokenResponse:
        """Verify OTP and login/register student."""

        otp_repository = OTPRepository(db)
        otp_service = OTPService(otp_repository)

        is_valid = await otp_service.verify_otp(
            mobile=mobile,
            otp=otp,
        )

        if not is_valid:
            raise UnauthorizedException(
                "Invalid or expired OTP."
            )

        user = await self.user_repository.get_by_mobile(
            db,
            mobile,
        )

        if user is None:

            user = User(
                id=gen_id(),
                email=f"{mobile}@student.example.com",
                hashed_password="",
                name="Student",
                role="student",
                xp=0,
                streak_count=0,
                avatar_url=None,
                mobile=mobile,
                google_id=None,
                profile_image=None,
                login_provider="mobile",
                is_mobile_verified=True,
                is_email_verified=False,
            )

            await self.user_repository.create(
                db,
                user,
            )

        else:

            user.is_mobile_verified = True

            await self.user_repository.update(
                db,
                user,
            )

        access_token = create_access_token(
            {
                "sub": user.id,
                "role": user.role,
            }
        )

        return TokenResponse(
            access_token=access_token,
            user=self._build_public_user(user),
        )

    async def google_login(
        self,
        db: AsyncSession,
        token: str,
    ) -> TokenResponse:
        """Verify Google ID token and login/register user."""

        try:

            google_user = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )

        except ValueError:

            raise UnauthorizedException(
                "Invalid Google token"
            )

        google_id = google_user.get("sub")
        email = google_user.get("email")
        name = google_user.get(
            "name",
            "Student",
        )

        if not google_id or not email:

            raise UnauthorizedException(
                "Invalid Google account information"
            )

        user = await self.user_repository.get_by_email(
            db,
            email,
        )

        if user is None:

            user = User(
                id=gen_id(),
                email=email,
                hashed_password="",
                name=name,
                role="student",
                xp=0,
                streak_count=0,
                avatar_url=google_user.get("picture"),
                mobile=None,
                google_id=google_id,
                profile_image=google_user.get("picture"),
                login_provider="google",
                is_mobile_verified=False,
                is_email_verified=True,
            )

            await self.user_repository.create(
                db,
                user,
            )

        else:

            user.google_id = google_id
            user.login_provider = "google"

            if google_user.get("picture"):

                user.avatar_url = google_user.get("picture")
                user.profile_image = google_user.get("picture")

            await self.user_repository.update(
                db,
                user,
            )

        access_token = create_access_token(
            {
                "sub": user.id,
                "role": user.role,
            }
        )

        return TokenResponse(
            access_token=access_token,
            user=self._build_public_user(user),
        )


# Create AuthService object
auth_service = AuthService()