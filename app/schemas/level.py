from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


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
    xp_reward: int = 100
    pass_percentage: int = 70
    estimated_minutes: int = 20
    video_url: Optional[str] = None
    video_duration_seconds: int = 1200
    theory_html: str = ""
    notes_url: Optional[str] = None


class LevelCreate(LevelBase):
    pass


class Level(LevelBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime