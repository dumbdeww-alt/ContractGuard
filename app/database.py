from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import get_settings

settings = get_settings()

db_url = settings.get_database_url()
engine_kwargs = {"pool_pre_ping": True}
if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    db_url,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a transactional database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
