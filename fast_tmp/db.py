from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from fast_tmp.conf import settings

SessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    future=True,
    bind=create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG),
)


async def get_db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
