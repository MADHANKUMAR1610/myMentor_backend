"""Application schema exports."""

from app.schemas.auth import (
    LoginRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    GoogleLoginRequest,
    TokenResponse,
    UserCreate,
    UserPublic,
)
from app.schemas.challenge import (
    Challenge,
    ChallengeBase,
    ChallengeCreate,
    Checkpoint,
    CheckpointBase,
    CheckpointCreate,
    TestCase,
)
from app.schemas.code_execution import (
    RunRequest,
    RunResult,
    SubmissionRequest,
    SubmissionResult,
    TestCaseResult,
)
from app.schemas.common import (
    gen_id,
    utc_now_iso,
)
from app.schemas.course import (
    Course,
    CourseBase,
    CourseCreate,
)
from app.schemas.level import (
    Level,
    LevelBase,
    LevelCreate,
    StageName,
)
from app.schemas.progress import (
    CheckpointProgress,
    LevelProgress,
    Enrollment,
    CompleteCheckpointRequest,
    VideoProgressRequest,
    CompleteLevelRequest,
)
from app.schemas.response import ApiResponse
from app.schemas.career_path import (
    CareerProfileCreate,
    CareerProfileResponse,
    CareerReportResponse,
    CareerRoadmapResponse,
)
from app.schemas.career_path import (
    CareerPathRequest,
    CareerPathResponse,
)
__all__ = [
    "LoginRequest",
    "SendOTPRequest",
    "VerifyOTPRequest",
    "GoogleLoginRequest",
    "TokenResponse",
    "UserCreate",
    "UserPublic",

    "Challenge",
    "ChallengeBase",
    "ChallengeCreate",
    "Checkpoint",
    "CheckpointBase",
    "CheckpointCreate",
    "TestCase",

    "RunRequest",
    "RunResult",
    "SubmissionRequest",
    "SubmissionResult",
    "TestCaseResult",

    "gen_id",
    "utc_now_iso",

    "Course",
    "CourseBase",
    "CourseCreate",

    "Level",
    "LevelBase",
    "LevelCreate",
    "StageName",

    "CheckpointProgress",
    "Enrollment",
    "LevelProgress",
]