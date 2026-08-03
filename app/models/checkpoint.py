"""Checkpoint model."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    level_id: Mapped[str] = mapped_column(
        ForeignKey("levels.id"),
    )

    order: Mapped[int]

    timestamp_seconds: Mapped[int]

    challenge_id: Mapped[str] = mapped_column(
        ForeignKey("challenges.id"),
    )