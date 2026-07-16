"""JWT authentication utilities."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.repositories import user_repository

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def hash_password(
    password: str,
) -> str:
    """Hash a plain-text password."""

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    """Verify a password."""

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""

    expire = datetime.now(
        timezone.utc,
    ) + (
        expires_delta
        or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    )

    payload = data.copy()
    payload["exp"] = expire

    return jwt.encode(
        payload,
        settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(
    token: str,
) -> dict:
    """Decode a JWT."""

    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET.get_secret_value(),
            algorithms=[
                settings.JWT_ALGORITHM,
            ],
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme,
    ),
) -> dict:
    """Return authenticated user."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_token(
        credentials.credentials,
    )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await user_repository.get_public_by_id(
        user_id,
    )

    if not user:
        logger.warning(
            "User not found: %s",
            user_id,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_admin(
    user: dict = Depends(
        get_current_user,
    ),
) -> dict:
    """Return authenticated admin."""

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user