"""Course schemas."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.common import gen_id, utc_now_iso


class CourseBase(BaseModel):
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    language: str = "Python"
    difficulty: Literal[
        "Beginner",
        "Intermediate",
        "Advanced",
    ] = "Beginner"
    duration_hours: int = 10
    status: Literal["draft", "published"] = "published"


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: str = Field(default_factory=gen_id)
    created_at: str = Field(default_factory=utc_now_iso)