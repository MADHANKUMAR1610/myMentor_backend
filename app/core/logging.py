"""
Application logging configuration.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "application.log"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)


def setup_logging() -> None:
    """Configure application logging."""

    formatter = logging.Formatter(
        LOG_FORMAT,
    )

    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=(
            logging.DEBUG
            if settings.DEBUG
            else logging.INFO
        ),
        handlers=[
            console_handler,
            file_handler,
        ],
        force=True,
    )

    logging.getLogger("uvicorn.access").setLevel(
        logging.WARNING
    )