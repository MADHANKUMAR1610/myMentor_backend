"""Level schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.common import gen_id, utc_now_iso


StageName = Literal[
    "Beginner",
    "Intermediate",
    "Expert",
]


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