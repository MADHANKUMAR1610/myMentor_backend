"""Authentication API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database.postgres import get_db
from app.schemas import (
    ApiResponse,
    LoginRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    GoogleLoginRequest,
    TokenResponse,
    UserCreate,
    UserPublic,
)
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:

    result = await auth_service.register(
        db,
        payload,
    )

    return ApiResponse(
        message="User registered successfully",
        data=result,
    )


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Login",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:

    result = await auth_service.login(
        db,
        payload,
    )

    return ApiResponse(
        message="Login successful",
        data=result,
    )


@router.post(
    "/student/send-otp",
    status_code=status.HTTP_200_OK,
)
async def send_student_otp(
    payload: SendOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    print(
        "AUTH ROUTE HIT",
        flush=True,
    )

    result = await auth_service.send_otp(
        db,
        payload.mobile,
    )

    return ApiResponse(
        message="OTP sent successfully",
        data=result,
    )


@router.post(
    "/student/verify-otp",
    response_model=ApiResponse[TokenResponse],
)
async def verify_student_otp(
    payload: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
):

    result = await auth_service.verify_otp(
        db,
        payload.mobile,
        payload.otp,
    )

    return ApiResponse(
        message="Student login successful",
        data=result,
    )


@router.post(
    "/student/google",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def student_google_login(
    payload: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:

    result = await auth_service.google_login(
        db,
        payload.token,
    )

    return ApiResponse(
        message="Google login successful",
        data=result,
    )
@router.get(
    "/me",
    response_model=ApiResponse[UserPublic],
)
async def get_me(
    current_user=Depends(get_current_user),
) -> ApiResponse[UserPublic]:

    user = auth_service.get_current_user_response(
        current_user,
    )

    return ApiResponse(
        message="User profile retrieved successfully",
        data=user,
    )