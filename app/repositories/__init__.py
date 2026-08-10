"""Application repositories."""

from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.level_repository import LevelRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.user_repository import UserRepository
from app.repositories.career_path_repository import CareerPathRepository
from .otp_repository import OTPRepository
__all__ = [
    "ChallengeRepository",
    "CourseRepository",
    "LevelRepository",
    "ProgressRepository",
    "UserRepository",
    "CareerPathRepository",
]