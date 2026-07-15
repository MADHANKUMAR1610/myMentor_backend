"""Pydantic models for Digipin Academy."""
from datetime import datetime, timezone
from typing import List, Optional, Literal
import uuid
from pydantic import BaseModel, Field, EmailStr, ConfigDict


def gen_id() -> str:
    return str(uuid.uuid4())


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------- Auth ----------
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


# ---------- Course ----------
class CourseBase(BaseModel):
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    language: str = "Python"
    difficulty: Literal["Beginner", "Intermediate", "Advanced"] = "Beginner"
    duration_hours: int = 10
    status: Literal["draft", "published"] = "published"


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: str = Field(default_factory=gen_id)
    created_at: str = Field(default_factory=utc_now_iso)


# ---------- Stage / Level ----------
StageName = Literal["Beginner", "Intermediate", "Expert"]


class LevelBase(BaseModel):
    course_id: str
    stage: StageName
    level_number: int
    title: str
    description: str = ""
    learning_objectives: List[str] = []
    xp_reward: int = 100
    pass_percentage: int = 70
    estimated_minutes: int = 20
    video_url: Optional[str] = None
    video_duration_seconds: int = 1200
    theory_html: str = ""
    notes_url: Optional[str] = None
    resources: List[dict] = []


class LevelCreate(LevelBase):
    pass


class Level(LevelBase):
    id: str = Field(default_factory=gen_id)
    created_at: str = Field(default_factory=utc_now_iso)


# ---------- Challenge ----------
class TestCase(BaseModel):
    input: str = ""
    expected_output: str
    is_hidden: bool = False


class ChallengeBase(BaseModel):
    title: str
    business_scenario: str = ""
    problem_statement: str
    difficulty: Literal["Easy", "Medium", "Hard"] = "Easy"
    language: str = "python"
    starter_code: str = ""
    expected_output: str = ""
    constraints: str = ""
    hints: List[str] = []
    solution: str = ""
    explanation: str = ""
    marks: int = 10
    xp: int = 50
    retry_limit: int = 5
    test_cases: List[TestCase] = []


class ChallengeCreate(ChallengeBase):
    pass


class Challenge(ChallengeBase):
    id: str = Field(default_factory=gen_id)


# ---------- Checkpoint ----------
class CheckpointBase(BaseModel):
    level_id: str
    order: int  # 1..4
    timestamp_seconds: int
    challenge_id: str


class CheckpointCreate(CheckpointBase):
    pass


class Checkpoint(CheckpointBase):
    id: str = Field(default_factory=gen_id)


# ---------- Progress ----------
class CheckpointProgress(BaseModel):
    checkpoint_id: str
    completed: bool = False
    submissions: int = 0
    completed_at: Optional[str] = None


class LevelProgress(BaseModel):
    id: str = Field(default_factory=gen_id)
    user_id: str
    level_id: str
    course_id: str
    video_watched_seconds: int = 0
    video_completed: bool = False
    checkpoints: List[CheckpointProgress] = []
    completed: bool = False
    completed_at: Optional[str] = None
    xp_earned: int = 0
    updated_at: str = Field(default_factory=utc_now_iso)


# ---------- Enrollment ----------
class Enrollment(BaseModel):
    id: str = Field(default_factory=gen_id)
    user_id: str
    course_id: str
    enrolled_at: str = Field(default_factory=utc_now_iso)


# ---------- Submission ----------
class SubmissionRequest(BaseModel):
    challenge_id: str
    language: str
    source_code: str
    stdin: Optional[str] = ""


class TestCaseResult(BaseModel):
    input: str
    expected: str
    actual: str
    passed: bool
    is_hidden: bool = False


class SubmissionResult(BaseModel):
    passed: bool
    stdout: str = ""
    stderr: str = ""
    time_ms: int = 0
    test_results: List[TestCaseResult] = []
    passed_count: int = 0
    total_count: int = 0
    xp_earned: int = 0


class RunRequest(BaseModel):
    language: str
    source_code: str
    stdin: Optional[str] = ""


class RunResult(BaseModel):
    stdout: str = ""
    stderr: str = ""
    time_ms: int = 0
