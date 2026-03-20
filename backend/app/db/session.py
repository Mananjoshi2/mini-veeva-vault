from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings


def get_engine(settings: Settings):
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def get_sessionmaker(settings: Settings):
    engine = get_engine(settings)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

