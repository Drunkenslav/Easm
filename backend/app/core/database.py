"""
Database connection and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings


# Convert sync database URL to async
def get_async_database_url(url: str) -> str:
    """Convert sync database URL to async version"""
    if url.startswith("sqlite"):
        # SQLite: sqlite:/// -> sqlite+aiosqlite:///
        return url.replace("sqlite://", "sqlite+aiosqlite://")
    elif "postgresql" in url and "asyncpg" not in url:
        # PostgreSQL: postgresql:// -> postgresql+asyncpg://
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


# Create async engine
async_database_url = get_async_database_url(settings.database_url)
engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
