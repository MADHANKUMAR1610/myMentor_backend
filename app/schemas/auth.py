"""Authentication request and response schemas."""
from pydantic import BaseModel
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr

class UserPublic(BaseModel):
    id: str
    email: str
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


class SendOTPRequest(BaseModel):
    mobile: str


class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str


class GoogleLoginRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic