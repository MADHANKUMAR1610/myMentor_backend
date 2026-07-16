"""Application repositories."""

from app.repositories.challenge_repository import (
    challenge_repository,
)
from app.repositories.course_repository import (
    course_repository,
)
from app.repositories.level_repository import (
    level_repository,
)
from app.repositories.progress_repository import (
    progress_repository,
)
from app.repositories.user_repository import (
    user_repository,
)
from app.repositories.admin_repository import (
    admin_repository,
)

__all__ = [
    "challenge_repository",
    "course_repository",
    "level_repository",
    "progress_repository",
    "user_repository",
]