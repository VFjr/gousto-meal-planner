import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

# Get the DATABASE_URL from environment variable, fallback to localhost if not set
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@localhost:5432/{os.getenv('POSTGRES_DB')}"
)

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)


# Provide an async session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session
