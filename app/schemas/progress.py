"""Student progress and enrollment schemas."""

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import (
    gen_id,
    utc_now_iso,
)


class CheckpointProgress(BaseModel):
    """Checkpoint completion progress."""

    checkpoint_id: str
    completed: bool = False
    submissions: int = 0
    completed_at: Optional[str] = None


class LevelProgress(BaseModel):
    """Student progress for a course level."""

    id: str = Field(
        default_factory=gen_id
    )
    user_id: str
    level_id: str
    course_id: str
    video_watched_seconds: int = 0
    video_completed: bool = False
    checkpoints: list[CheckpointProgress] = Field(
        default_factory=list
    )
    completed: bool = False
    completed_at: Optional[str] = None
    xp_earned: int = 0
    updated_at: str = Field(
        default_factory=utc_now_iso
    )


class Enrollment(BaseModel):
    """Student course enrollment."""

    id: str = Field(
        default_factory=gen_id
    )
    user_id: str
    course_id: str
    enrolled_at: str = Field(
        default_factory=utc_now_iso
    )
    # -----------------------------
# Request Models
# -----------------------------

class CompleteCheckpointRequest(BaseModel):
    """Complete a checkpoint."""

    level_id: str
    checkpoint_id: str


class VideoProgressRequest(BaseModel):
    """Update watched video progress."""

    level_id: str
    watched_seconds: int


class CompleteLevelRequest(BaseModel):
    """Complete a level."""

    level_id: str