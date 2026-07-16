"""Code execution schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class SubmissionRequest(BaseModel):
    """Code submission request."""

    challenge_id: str
    language: str
    source_code: str
    stdin: Optional[str] = ""


class TestCaseResult(BaseModel):
    """Individual test case execution result."""

    input: str
    expected: str
    actual: str
    passed: bool
    is_hidden: bool = False


class SubmissionResult(BaseModel):
    """Code submission evaluation result."""

    passed: bool
    stdout: str = ""
    stderr: str = ""
    time_ms: int = 0
    test_results: list[TestCaseResult] = Field(
        default_factory=list
    )
    passed_count: int = 0
    total_count: int = 0
    xp_earned: int = 0


class RunRequest(BaseModel):
    """Code execution request."""

    language: str
    source_code: str
    stdin: Optional[str] = ""


class RunResult(BaseModel):
    """Code execution result."""

    stdout: str = ""
    stderr: str = ""
    time_ms: int = 0