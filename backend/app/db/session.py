from collections.abc import AsyncIterator
from datetime import UTC, datetime

from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()


def make_async_database_url(database_url: str) -> URL:
    url = make_url(database_url)
    if not url.drivername.startswith("postgresql"):
        raise ValueError("AGROGUARD_DATABASE_URL must be a PostgreSQL connection URL")

    query = dict(url.query)
    sslmode = query.pop("sslmode", None)
    if sslmode and "ssl" not in query:
        query["ssl"] = sslmode

    return url.set(drivername="postgresql+asyncpg", query=query)


_async_url = make_async_database_url(settings.database_url)

engine = create_async_engine(
    _async_url,
    pool_pre_ping=True,
)
session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


def utcnow() -> datetime:
    return datetime.now(UTC)
