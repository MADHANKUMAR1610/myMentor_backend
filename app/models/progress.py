from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Progress(Base):
    __tablename__ = "level_progress"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
    )

    level_id: Mapped[str] = mapped_column(
        ForeignKey("levels.id"),
    )

    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id"),
    )

    video_watched_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    video_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    xp_earned: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # NEW
    checkpoints: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    # NEW
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )