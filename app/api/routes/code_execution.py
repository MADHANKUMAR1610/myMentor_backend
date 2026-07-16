"""Code execution API routes."""

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.core.auth import get_current_user
from app.schemas import (
    ApiResponse,
    RunRequest,
    RunResult,
    SubmissionRequest,
    SubmissionResult,
)
from app.services import code_execution_service


router = APIRouter(
    prefix="/code",
    tags=["Code Execution"],
)


@router.post(
    "/run",
    response_model=ApiResponse[RunResult],
    status_code=status.HTTP_200_OK,
    summary="Run source code",
    description=(
        "Execute source code without evaluating "
        "against challenge test cases."
    ),
)
async def run_code(
    request: RunRequest,
    _user: dict = Depends(get_current_user),
) -> ApiResponse[RunResult]:
    """Execute source code."""

    result = await code_execution_service.run_code(
        request,
    )

    return ApiResponse(
        message="Code executed successfully",
        data=result,
    )


@router.post(
    "/submit",
    response_model=ApiResponse[SubmissionResult],
    status_code=status.HTTP_200_OK,
    summary="Submit challenge solution",
    description=(
        "Evaluate submitted source code against "
        "the challenge test cases and return the "
        "submission result."
    ),
)
async def submit_code(
    request: SubmissionRequest,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[SubmissionResult]:
    """Submit code for challenge evaluation."""

    result = await code_execution_service.submit_code(
        request,
        current_user["id"],
    )

    return ApiResponse(
        message="Code submitted successfully",
        data=result,
    )