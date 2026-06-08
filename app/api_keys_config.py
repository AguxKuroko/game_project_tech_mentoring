from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigApp(BaseSettings):
    RAWG_API_KEY: str
    OPEN_AI_API_KEY: str
    BACKEND_API_KEY: str
    LOGFIRE_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_api_keys() -> ConfigApp:
    return ConfigApp()
