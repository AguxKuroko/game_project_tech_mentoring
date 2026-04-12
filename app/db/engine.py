from functools import lru_cache

from sqlmodel import create_engine

from app.db.db_config import db_settings


@lru_cache
def get_engine():
    return create_engine(db_settings.database_url, echo=True)


engine = get_engine()
