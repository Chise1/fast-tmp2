from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fast_tmp.conf import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    future=True,
    bind=engine,
)


def get_db_session() -> Session:
    with SessionLocal() as session:
        yield session
