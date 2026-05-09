from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings


def _build_engine() -> AsyncEngine:
    return create_async_engine(get_settings().database_url, future=True, echo=False)


def _build_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Lazy module-level singletons; disposed/rebuilt by reset_engine().
engine: AsyncEngine = _build_engine()
session_factory: async_sessionmaker[AsyncSession] = _build_factory(engine)


async def reset_engine() -> None:
    """Dispose the current engine and replace globals with a fresh one.

    Used by the lifespan shutdown so subsequent test reuses don't run into
    asyncpg "another operation in progress" errors caused by pool entries
    from a stale event loop.
    """
    global engine, session_factory
    try:
        await engine.dispose()
    except Exception:
        pass
    engine = _build_engine()
    session_factory = _build_factory(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
