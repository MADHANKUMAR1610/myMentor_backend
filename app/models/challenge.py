"""Challenge model."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    title: Mapped[str]

    business_scenario: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    problem_statement: Mapped[str] = mapped_column(
        Text,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="Easy",
    )

    language: Mapped[str] = mapped_column(
        String(50),
        default="python",
    )

    starter_code: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    expected_output: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    constraints: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    hints: Mapped[list] = mapped_column(
        JSONB,
        default=list,
    )

    solution: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    marks: Mapped[int] = mapped_column(
        Integer,
        default=10,
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        default=50,
    )

    retry_limit: Mapped[int] = mapped_column(
        Integer,
        default=5,
    )

    test_cases: Mapped[list] = mapped_column(
        JSONB,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )