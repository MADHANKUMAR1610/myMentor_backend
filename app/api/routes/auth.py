"""Authentication API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.core.auth import get_current_user
from app.schemas import (
    ApiResponse,
    LoginRequest,
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
    description="Create a new student or admin account and return an access token.",
)
async def register(
    payload: UserCreate,
) -> ApiResponse[TokenResponse]:
    """Register a new user."""

    result = await auth_service.register(
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
    description="Authenticate a user and return a JWT access token.",
)
async def login(
    payload: LoginRequest,
) -> ApiResponse[TokenResponse]:
    """Authenticate a user."""

    result = await auth_service.login(
        payload,
    )

    return ApiResponse(
        message="Login successful",
        data=result,
    )


@router.get(
    "/me",
    response_model=ApiResponse[UserPublic],
    status_code=status.HTTP_200_OK,
    summary="Current user",
    description="Return the authenticated user's profile.",
)
async def get_me(
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[UserPublic]:
    """Return the authenticated user."""

    user = auth_service.get_current_user_response(
        current_user,
    )

    return ApiResponse(
        message="User profile retrieved successfully",
        data=user,
    )