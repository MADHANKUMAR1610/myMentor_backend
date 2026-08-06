from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    DateTime,
    func,
)

from app.database.base import Base
import uuid

class CareerProfile(Base):
    __tablename__ = "career_profiles"

  
    id = Column(
    String(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
)
    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
    )

    career_goal = Column(
        String(255),
        nullable=False,
    )

    full_name = Column(
        String(255),
        nullable=False,
    )

    date_of_birth = Column(
        Date,
        nullable=False,
    )

    education_stage = Column(
        String(100),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )