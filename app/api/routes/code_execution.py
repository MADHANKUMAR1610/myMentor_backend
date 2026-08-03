"""Code execution API routes."""

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
    RunRequest,
    RunResult,
    SubmissionRequest,
    SubmissionResult,
)
from app.services.code_execution_service import CodeExecutionService

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
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> ApiResponse[RunResult]:
    """Execute source code."""

    service = CodeExecutionService(db)

    result = await service.run_code(
        request,
    )

    return ApiResponse(
        message="Code executed successfully",
        data=result,
    )


@router.post("/submit")
async def submit_code(
    request: SubmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        print("========== API HIT ==========")
        print("User:", current_user)

        service = CodeExecutionService(db)

        result = await service.submit_code(
            request,
            current_user.id,   # Use .id, not ["id"]
        )

        return ApiResponse(
            message="Success",
            data=result,
        )

    except Exception as e:
        print("========== EXCEPTION ==========")
        traceback.print_exc()
        print("ERROR:", repr(e))
        raise