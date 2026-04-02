from sqlmodel import create_engine

from app.db.db_config import db_settings

engine = create_engine(db_settings.database_url, echo=True)
