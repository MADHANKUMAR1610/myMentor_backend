import asyncio
from sqlalchemy import text
from app.database import engine

async def update():
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE challenges
            ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
        """))

        await conn.execute(text("""
            ALTER TABLE challenges
            ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
        """))

asyncio.run(update())