from pydantic_settings import BaseSettings

from app.app_config import app_paths

DB_NAME = "worst_game.db"


class DatabaseSettings(BaseSettings):
    db_name: str = DB_NAME

    @property
    def database_url(self) -> str:
        return f"sqlite:///{(app_paths.db_dir / self.db_name).as_posix()}"


db_settings = DatabaseSettings()
