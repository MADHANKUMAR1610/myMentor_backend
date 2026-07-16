"""Authentication request and response schemas."""

from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: Literal["admin", "student"]
    xp: int = 0
    streak_count: int = 0
    avatar_url: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Literal["admin", "student"] = "student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic