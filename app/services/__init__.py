"""Application services."""

from app.services.auth_service import auth_service
from app.services.challenge_service import (
    challenge_service,
)
from app.services.code_execution_service import (
    code_execution_service,
)
from app.services.course_service import course_service
from app.services.level_service import level_service
from app.services.progress_service import (
    progress_service,
)
from app.services.admin_service import (
    admin_service,
)
from app.services.certificate_service import (
    certificate_service,
)

__all__ = [
    "auth_service",
    "challenge_service",
    "code_execution_service",
    "course_service",
    "level_service",
    "progress_service",
]