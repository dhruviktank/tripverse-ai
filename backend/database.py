"""Database connection setup using async SQLAlchemy with Neon Postgres."""

import ssl as _ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import get_settings

settings = get_settings()


def _build_asyncpg_url(raw_url: str) -> tuple[str, dict]:
    """Convert a standard postgres:// URL to one compatible with asyncpg.

    asyncpg doesn't understand 'sslmode' or 'channel_binding' query params,
    so we strip them and pass SSL via connect_args instead.
    """
    # Swap scheme to postgresql+asyncpg
    url = raw_url.strip().strip("'\"")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Parse and clean query params
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    # Determine if SSL is needed
    needs_ssl = params.pop("sslmode", [None])[0] in ("require", "verify-full", "verify-ca", "prefer")
    # Remove channel_binding (asyncpg doesn't support it)
    params.pop("channel_binding", None)

    # Rebuild the URL without incompatible params
    clean_query = urlencode({k: v[0] for k, v in params.items()}, doseq=False)
    clean_url = urlunparse(parsed._replace(query=clean_query))

    connect_args: dict = {}
    if needs_ssl:
        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx

    return clean_url, connect_args


_db_url, _connect_args = _build_asyncpg_url(settings.database_url)

engine = create_async_engine(
    _db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db():
    """FastAPI dependency that provides DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
