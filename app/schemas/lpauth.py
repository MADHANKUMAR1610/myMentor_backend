from pydantic import BaseModel


class SendOTPRequest(BaseModel):
    mobile: str


class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    mobile: str | None = None
    email: str | None = None