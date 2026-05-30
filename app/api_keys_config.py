from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigApp(BaseSettings):
    RAWG_API_KEY: str
    OPEN_AI_API_KEY: str
    BACKEND_API_KEY: str
    LOGFIRE_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env")


api_game_key = ConfigApp()
