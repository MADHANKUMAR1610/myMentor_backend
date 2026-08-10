from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
    )

    name: Mapped[str] = mapped_column(
        String(100),
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="student",
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    streak_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    mobile: Mapped[str | None] = mapped_column(
        String(15),
        unique=True,
        nullable=True,
    )

    google_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    profile_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    login_provider: Mapped[str] = mapped_column(
        String(20),
        default="email",
    )

    is_mobile_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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


print("MODEL FILE:", __file__)
print(User.__table__.columns.keys())