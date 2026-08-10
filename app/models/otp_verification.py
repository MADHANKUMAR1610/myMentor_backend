from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    mobile: Mapped[str] = mapped_column(
        String(15),
        index=True,
    )

    otp: Mapped[str] = mapped_column(
        String(6),
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )