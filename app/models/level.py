from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Level(Base):
    __tablename__ = "levels"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id"),
    )

    stage: Mapped[str]

    level_number: Mapped[int]

    title: Mapped[str]

    description: Mapped[str] = mapped_column(Text)

    xp_reward: Mapped[int]

    pass_percentage: Mapped[int]

    estimated_minutes: Mapped[int]

    video_url: Mapped[str | None]

    video_duration_seconds: Mapped[int]

    theory_html: Mapped[str]

    notes_url: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )