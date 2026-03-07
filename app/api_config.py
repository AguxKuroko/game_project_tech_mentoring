from pydantic_settings import BaseSettings,SettingsConfigDict

class ConfigApp(BaseSettings):
    RAWG_API_KEY : str

    model_config = SettingsConfigDict(env_file=".env")

api_game_key = ConfigApp()
