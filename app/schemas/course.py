from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

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
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime