from pydantic_settings import BaseSettings

from app.app_config import app_paths


class DatabaseSettings(BaseSettings):
    database_url: str = f"sqlite:///{(app_paths.db_dir / 'worst_game.db').as_posix()}"


db_settings = DatabaseSettings()
