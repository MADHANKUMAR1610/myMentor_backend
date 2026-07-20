"""MongoDB connection shared across the app."""

from pathlib import Path


from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).parent
from app.core.config import settings

url = settings.DATABASE_URL
db_name = settings.DATABASE_NAME

client = AsyncIOMotorClient(
    settings.DATABASE_URL,
)

db = client[
    settings.DATABASE_NAME
]
