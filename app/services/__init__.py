"""Application services."""

from app.services.admin_service import AdminService
from app.services.auth_service import auth_service
from app.services.certificate_service import CertificateService
from app.services.challenge_service import ChallengeService
from app.services.code_execution_service import CodeExecutionService
from app.services.course_service import CourseService
from app.services.level_service import LevelService
from app.services.progress_service import ProgressService
from app.services.gemini_service import (
    GeminiService,
    gemini_service,
)

__all__ = [
    "auth_service",
    "AdminService",
    "CertificateService",
    "ChallengeService",
    "CodeExecutionService",
    "CourseService",
    "LevelService",
    "ProgressService",
    "GeminiService",
    "gemini_service",
]