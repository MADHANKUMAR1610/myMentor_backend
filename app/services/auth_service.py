"""Authentication business logic."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

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


auth_service = AuthService()