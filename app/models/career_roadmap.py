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

class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(
    String(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
)

    report_id = Column(
    String(36),
    ForeignKey("career_reports.id"),
    nullable=False,
)

    phase_number = Column(
        Integer,
        nullable=False,
    )

    phase_title = Column(
        String(255),
        nullable=False,
    )

    duration = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )