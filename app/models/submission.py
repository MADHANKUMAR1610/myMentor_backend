from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    challenge_id: Mapped[str] = mapped_column(
        ForeignKey("challenges.id"),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    stdout: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    stderr: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    passed_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    xp_earned: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    time_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )