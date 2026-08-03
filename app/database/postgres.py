"""PostgreSQL connection management."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Create PostgreSQL engine
engine = create_async_engine(
    settings.POSTGRES_DATABASE_URL,
    echo=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Yield a PostgreSQL session."""
    async with AsyncSessionLocal() as session:
        yield session