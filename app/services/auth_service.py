"""Authentication business logic."""

import logging

from app.core.auth import(
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import (
    BadRequestException,
    UnauthorizedException,
)
from app.repositories import user_repository
from app.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserPublic,
    gen_id,
    utc_now_iso,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Handle authentication and user registration."""

    def __init__(self) -> None:
        self.user_repository = user_repository

    def _build_public_user(
        self,
        user: dict,
    ) -> UserPublic:
        """Convert database user document to public response."""

        return UserPublic(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            xp=user.get("xp", 0),
            streak_count=user.get(
                "streak_count",
                0,
            ),
            avatar_url=user.get("avatar_url"),
        )

    async def register(
        self,
        payload: UserCreate,
    ) -> TokenResponse:
        """Register a new user."""

        logger.info(
            "Registration attempt for email: %s",
            payload.email,
        )

        existing_user = (
            await self.user_repository.get_by_email(
                payload.email
            )
        )

        if existing_user:
            logger.warning(
                "Registration failed. Email already exists: %s",
                payload.email,
            )

            raise BadRequestException(
                "Email already registered"
            )

        user_id = gen_id()

        user_document = {
            "id": user_id,
            "email": payload.email,
            "hashed_password": hash_password(
                payload.password
            ),
            "name": payload.name,
            "role": payload.role,
            "xp": 0,
            "streak_count": 0,
            "avatar_url": None,
            "created_at": utc_now_iso(),
        }

        await self.user_repository.create(
            user_document
        )

        access_token = create_access_token(
            {
                "sub": user_id,
                "role": payload.role,
            }
        )

        logger.info(
            "User registered successfully. User ID: %s",
            user_id,
        )

        return TokenResponse(
            access_token=access_token,
            user=self._build_public_user(
                user_document
            ),
        )

    async def login(
        self,
        payload: LoginRequest,
    ) -> TokenResponse:
        """Authenticate a user and return JWT."""

        logger.info(
            "Login attempt for email: %s",
            payload.email,
        )

        user = await self.user_repository.get_by_email(
            payload.email
        )

        if (
            not user
            or not verify_password(
                payload.password,
                user["hashed_password"],
            )
        ):
            logger.warning(
                "Invalid login attempt for email: %s",
                payload.email,
            )

            raise UnauthorizedException(
                "Invalid credentials"
            )

        access_token = create_access_token(
            {
                "sub": user["id"],
                "role": user["role"],
            }
        )

        logger.info(
            "Login successful. User ID: %s",
            user["id"],
        )

        return TokenResponse(
            access_token=access_token,
            user=self._build_public_user(
                user
            ),
        )

    def get_current_user_response(
        self,
        user: dict,
    ) -> UserPublic:
        """Return authenticated user's public profile."""

        return self._build_public_user(
            user
        )


auth_service = AuthService()