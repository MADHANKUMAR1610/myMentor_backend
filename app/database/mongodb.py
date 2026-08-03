"""MongoDB connection management."""

import logging
from typing import Optional

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_database() -> None:
    """Initialize the MongoDB connection."""

    global _client
    global _database

    if _client is not None:
        logger.debug(
            "MongoDB connection already initialized",
        )
        return

    logger.info("Connecting to MongoDB")

    try:
        _client = AsyncIOMotorClient(
           settings.MONGO_DATABASE_URL,
            serverSelectionTimeoutMS=5000,
        )

        await _client.admin.command(
            "ping",
        )

        _database = _client[
           settings.MONGO_DATABASE_URL
        ]

        logger.info(
            "MongoDB connected successfully",
        )

    except Exception:
        logger.exception(
            "Failed to connect to MongoDB",
        )
        raise


async def close_database() -> None:
    """Close the MongoDB connection."""

    global _client
    global _database

    if _client is None:
        logger.debug(
            "MongoDB connection already closed",
        )
        return

    logger.info(
        "Closing MongoDB connection",
    )

    _client.close()

    _client = None
    _database = None

    logger.info(
        "MongoDB connection closed",
    )


def get_database() -> AsyncIOMotorDatabase:
    """Return the active MongoDB database."""

    if _database is None:
        logger.error(
            "Database requested before initialization",
        )

        raise RuntimeError(
            "Database connection has not been initialized",
        )

    return _database