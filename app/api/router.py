"""Main application API router."""

from fastapi import APIRouter

from app.api.routes.root import router as root_router
from app.api.routes.auth import router as auth_router
from app.api.routes.courses import router as courses_router
from app.api.routes.levels import router as levels_router
from app.api.routes.challenges import (
    challenge_router,
    checkpoint_router,
)
from app.api.routes.code_execution import (
    router as code_execution_router,
)
from app.api.routes.progress import router as progress_router
from app.api.routes.admin import router as admin_router
from app.api.routes.certificates import router as certificates_router
from app.api.routes.career import (
    router as career_router,
)

api_router = APIRouter()

api_router.include_router(root_router)
api_router.include_router(auth_router)
api_router.include_router(courses_router)
api_router.include_router(levels_router)
api_router.include_router(challenge_router)
api_router.include_router(checkpoint_router)
api_router.include_router(code_execution_router)
api_router.include_router(progress_router)
api_router.include_router(admin_router)
api_router.include_router(certificates_router)
api_router.include_router(
    career_router,
)