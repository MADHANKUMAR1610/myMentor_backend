from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    func,
)

from app.database.base import Base
import uuid

class CareerReport(Base):
    __tablename__ = "career_reports"

    id = Column(
    String(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
)
  
    profile_id = Column(
    String(36),
    ForeignKey("career_profiles.id"),
    nullable=False,
)
    career_persona = Column(
        String(255),
        nullable=False,
    )

    confidence_score = Column(
        Integer,
        nullable=False,
    )
    generated_by = Column(
    String(50),
    nullable=False,
    default="gemini",
)
    recommended_stream = Column(
        String(255),
        nullable=False,
    )

    primary_skill = Column(
        String(255),
        nullable=False,
    )

    career_overview = Column(
        Text,
        nullable=False,
    )

    next_step = Column(
        Text,
        nullable=False,
    )

    target_exams = Column(
        Text,
        nullable=True,
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