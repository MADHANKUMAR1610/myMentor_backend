"""Challenge and checkpoint schemas."""

from typing import List, Literal

from pydantic import BaseModel, Field

from app.schemas.common import gen_id


class TestCase(BaseModel):
    input: str = ""
    expected_output: str
    is_hidden: bool = False


class ChallengeBase(BaseModel):
    title: str
    business_scenario: str = ""
    problem_statement: str
    difficulty: Literal[
        "Easy",
        "Medium",
        "Hard",
    ] = "Easy"
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


class CheckpointBase(BaseModel):
    level_id: str
    order: int
    timestamp_seconds: int
    challenge_id: str


class CheckpointCreate(CheckpointBase):
    pass


class Checkpoint(CheckpointBase):
    id: str = Field(default_factory=gen_id)